# caishen-user-api

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

:warning: Added ModifiedPostgreSqlDsn on `settings.py` as a hack until pydantic gets updated because drivers are not yet permitted on PostgresDsn schemes. Example: `postgresql+asyncpg`

## Handling the Database

`ALEMBIC` is now being used to handle database migrations, so please make sure to use it instead of manually modifying the database.

To run alembic migrations to create the database before proceeding with development you should run the following command:

```python
alembic upgrade head
```

In case there is any doubt, go to [ALEMBIC Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) and check the instructions.

### SUPER_USER CONFIG

Before running the app, make sure to change the `SUPER_USER` configuration on `settings.py`, so you can login without any issues.
On startup, the api will check if `SUPER_USER_EMAIL` exists in the database and if it doesn't will populate the superuser automatically.

```python
    SUPER_USER_NAME: str = "admin"
    SUPER_USER_PASSWORD: str = "admin"
    SUPER_USER_EMAIL: EmailStr = "admin@example.com"  # type: ignore
    SUPER_USER_BIRTHDATE: date = date(2021, 9, 7)
```

### .env File

As this project uses pydantic BaseSettings, you can create a file called `.env` and populate it with the parameters defined in `settings.py` as you wish and this will populate the `Settings` class accordingly.
