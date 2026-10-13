"""
SupplyLens AI — Software Bill of Materials (SBOM) Ingestion Engine.

Supports:
- CycloneDX JSON (v1.3, v1.4, v1.5)
- SPDX JSON (v2.2, v2.3)
- Manual component creation

Features:
- Server-side validation and schema bounds
- PURL normalization and ecosystem inference
- Graph dependency edge extraction
- Graceful handling of missing or partial metadata
- Non-destructive idempotent parsing
"""
import json
import re
from typing import Any, Dict, List, Optional, Tuple


MAX_SBOM_BYTES = 10 * 1024 * 1024  # 10 MB upload ceiling


class SbomValidationError(Exception):
    pass


def detect_sbom_format(content: Any) -> str:
    """Determine whether the content is CycloneDX JSON, SPDX JSON, or unsupported."""
    if isinstance(content, dict):
        data = content
    elif isinstance(content, (str, bytes, bytearray)):
        try:
            data = json.loads(content)
        except Exception as e:
            raise SbomValidationError(f"Invalid JSON format: {str(e)}")
    else:
        raise SbomValidationError("Input must be a JSON string or dict object.")

    if not isinstance(data, dict):
        raise SbomValidationError("Root JSON entity must be an object.")

    if data.get("bomFormat") == "CycloneDX" or ("components" in data and "specVersion" in data):
        return "CYCLONEDX_JSON"

    if data.get("spdxVersion") or ("SPDXID" in data and "packages" in data):
        return "SPDX_JSON"

    # If it has components list without explicit bomFormat, check structure
    if "components" in data and isinstance(data["components"], list):
        return "CYCLONEDX_JSON"

    raise SbomValidationError(
        "Unsupported document format. SupplyLens accepts CycloneDX JSON or SPDX JSON manifests."
    )


def infer_ecosystem_from_purl(purl: Optional[str]) -> str:
    """Extract ecosystem from package-url format: pkg:<type>/<namespace>/<name>@<version>"""
    if not purl or not purl.startswith("pkg:"):
        return "generic"
    match = re.match(r"^pkg:([a-zA-Z0-9_\-\.]+)/", purl)
    if match:
        p_type = match.group(1).lower()
        mapping = {
            "npm": "npm",
            "pypi": "pypi",
            "maven": "maven",
            "golang": "golang",
            "cargo": "cargo",
            "nuget": "nuget",
            "gem": "rubygems",
            "composer": "packagist",
        }
        return mapping.get(p_type, p_type)
    return "generic"


def parse_cyclonedx_json(data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]], List[str]]:
    """
    Parse a CycloneDX JSON document.
    Returns:
      (components, dependency_edges_by_ref_or_name, warnings)
    """
    warnings: List[str] = []
    if "components" not in data:
        raise SbomValidationError("CycloneDX document missing required 'components' field.")
    raw_components = data.get("components", [])
    if not isinstance(raw_components, list):
        raise SbomValidationError("CycloneDX 'components' field must be an array.")

    components: List[Dict[str, Any]] = []
    ref_to_name: Dict[str, str] = {}

    for idx, c in enumerate(raw_components):
        if not isinstance(c, dict):
            warnings.append(f"Skipped non-object component at index {idx}")
            continue

        name = c.get("name")
        version = c.get("version", "unknown")
        if not name:
            warnings.append(f"Component at index {idx} lacks a name; skipping.")
            continue

        bom_ref = c.get("bom-ref") or f"{name}@{version}"
        ref_to_name[bom_ref] = name

        purl = c.get("purl")
        ecosystem = infer_ecosystem_from_purl(purl)

        # License detection
        license_name = "UNKNOWN"
        licenses = c.get("licenses", [])
        if licenses and isinstance(licenses, list):
            first = licenses[0]
            if isinstance(first, dict):
                lic_obj = first.get("license", {})
                license_name = lic_obj.get("id") or lic_obj.get("name") or "PROPRIETARY"

        supplier_info = c.get("supplier", {})
        supplier_name = supplier_info.get("name") if isinstance(supplier_info, dict) else None

        scope = c.get("scope", "runtime")

        components.append({
            "name": str(name).strip(),
            "version": str(version).strip(),
            "ecosystem": ecosystem,
            "purl": purl,
            "license": license_name,
            "supplier_name": supplier_name,
            "direct": True if scope == "required" or idx < 15 else False,
            "scope": scope,
            "bom_ref": bom_ref,
            "raw_metadata": {
                "type": c.get("type", "library"),
                "description": c.get("description", ""),
                "hashes": c.get("hashes", []),
            },
        })

    # Dependencies
    edges: List[Tuple[str, str]] = []
    raw_deps = data.get("dependencies", [])
    if isinstance(raw_deps, list):
        for dep in raw_deps:
            if not isinstance(dep, dict):
                continue
            parent_ref = dep.get("ref")
            parent_name = ref_to_name.get(parent_ref, parent_ref)
            depends_on = dep.get("dependsOn", [])
            if isinstance(depends_on, list):
                for child_ref in depends_on:
                    child_name = ref_to_name.get(child_ref, child_ref)
                    if parent_name and child_name:
                        edges.append((parent_name, child_name))

    return components, edges, warnings


def parse_spdx_json(data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]], List[str]]:
    """
    Parse an SPDX JSON document.
    Returns:
      (components, dependency_edges_by_name, warnings)
    """
    warnings: List[str] = []
    packages = data.get("packages", [])
    if not isinstance(packages, list):
        raise SbomValidationError("SPDX 'packages' field must be an array.")

    components: List[Dict[str, Any]] = []
    spdx_id_to_name: Dict[str, str] = {}

    for idx, pkg in enumerate(packages):
        if not isinstance(pkg, dict):
            continue
        name = pkg.get("name")
        version = pkg.get("versionInfo", "unknown")
        spdx_id = pkg.get("SPDXID", f"SPDXRef-pkg-{idx}")

        if not name:
            warnings.append(f"SPDX package at index {idx} lacks a name; skipping.")
            continue

        spdx_id_to_name[spdx_id] = name

        # Extract PURL from externalRefs
        purl = None
        for ref in pkg.get("externalRefs", []):
            if isinstance(ref, dict) and ref.get("referenceType") == "purl":
                purl = ref.get("referenceLocator")
                break

        ecosystem = infer_ecosystem_from_purl(purl)
        license_concluded = pkg.get("licenseConcluded") or pkg.get("licenseDeclared") or "UNKNOWN"
        supplier_raw = pkg.get("supplier", "")
        supplier_name = None
        if supplier_raw and "Organization:" in supplier_raw:
            supplier_name = supplier_raw.replace("Organization:", "").strip()
        elif supplier_raw and "Person:" in supplier_raw:
            supplier_name = supplier_raw.replace("Person:", "").strip()

        components.append({
            "name": str(name).strip(),
            "version": str(version).strip(),
            "ecosystem": ecosystem,
            "purl": purl,
            "license": str(license_concluded),
            "supplier_name": supplier_name,
            "direct": True if idx < 10 else False,
            "scope": "runtime",
            "bom_ref": spdx_id,
            "raw_metadata": {
                "downloadLocation": pkg.get("downloadLocation", "NOASSERTION"),
                "filesAnalyzed": pkg.get("filesAnalyzed", False),
            },
        })

    # Relationships
    edges: List[Tuple[str, str]] = []
    for rel in data.get("relationships", []):
        if not isinstance(rel, dict):
            continue
        rel_type = rel.get("relationshipType")
        elem_id = rel.get("spdxElementId")
        related_id = rel.get("relatedSpdxElement")
        if rel_type in ("DEPENDS_ON", "CONTAINS", "DEPENDENCY_OF") and elem_id and related_id:
            parent_name = spdx_id_to_name.get(elem_id, elem_id)
            child_name = spdx_id_to_name.get(related_id, related_id)
            if parent_name and child_name:
                edges.append((parent_name, child_name))

    return components, edges, warnings
