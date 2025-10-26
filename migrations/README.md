# Database Migrations

Alembic manages schema evolution for the AutoTrade V3 project. Revisions live
under `migrations/versions`. Generate a new migration after modifying SQLAlchemy
models:

```bash
poetry run alembic revision --autogenerate -m "describe change"
```

Apply migrations to the configured database URL:

```bash
poetry run alembic upgrade head
```

The Alembic environment automatically reads application settings so that the
`DATABASE_URL` or associated components defined in `.env` are respected.
