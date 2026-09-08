# Testing

Run backend domain tests:

```powershell
cd backend
python -m unittest discover -s tests
```

The focused tests cover normalized risk, non-negative inventory reservation, and invalid order-state rejection. API smoke tests exercise seeded startup, the Digital Twin projection, cyber posture, and orders.
