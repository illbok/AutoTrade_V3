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

## Database and cache configuration

The data layer targets PostgreSQL/TimescaleDB via SQLAlchemy's async engine.
Configuration is provided through environment variables consumed by the shared
settings module:

| Variable | Description | Default |
| --- | --- | --- |
| `DATABASE_URL` | Full SQLAlchemy connection URL | assembled from components |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | Components used when `DATABASE_URL` is omitted | `autotrade`, `autotrade`, `localhost`, `5432`, `autotrade` |
| `DB_ECHO` | Enable SQL echo logging | `false` |
| `REDIS_URL` | Optional Redis connection string | `redis://localhost:6379` |
| `REDIS_HOST`, `REDIS_PORT` | Components used when `REDIS_URL` is omitted | `localhost`, `6379` |
| `REDIS_DB` | Redis logical database | unset |
| `REDIS_SSL` | Enable TLS for Redis | `false` |

Run database migrations with Alembic after updating models:

```bash
poetry run alembic upgrade head
```

The Alembic environment automatically reads the same settings to resolve the
target database URL.
