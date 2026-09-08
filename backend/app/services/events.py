from typing import Any
from sqlalchemy.orm import Session
from app.models import Event


class EventService:
    @staticmethod
    def record(
        db: Session,
        event_type: str,
        category: str,
        entity_type: str,
        entity_id: str,
        description: str,
        facility_code: str | None = None,
        source: str = "SYSTEM",
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
    ) -> Event:
        event = Event(
            event_type=event_type, category=category, entity_type=entity_type,
            entity_id=str(entity_id), facility_code=facility_code, source=source,
            description=description, previous_state=previous_state, new_state=new_state,
        )
        db.add(event)
        return event

