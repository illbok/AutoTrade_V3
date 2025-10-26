# AutoTrade V3

AutoTrade V3 is an event-driven Bitcoin trading platform targeting the Upbit
exchange. The project follows the roadmap documented in [`docs/PLAN.md`](docs/PLAN.md)
and is implemented with Python 3.11, FastAPI, and Pydantic.

## Development quickstart

```bash
poetry install
poetry run uvicorn autotrade.app.main:app --reload
```

Visit `http://localhost:8000/health` to verify the service is running and
emitting both UTC and KST timestamps.
