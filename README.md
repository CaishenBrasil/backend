# caishen-user-api

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/CaishenBrasil/caishen-user-api/dev.svg)](https://results.pre-commit.ci/latest/github/CaishenBrasil/caishen-user-api/dev)

:warning: Added ModifiedPostgreSqlDsn on `settings.py` as a hack until pydantic gets updated because drivers are not yet permitted on PostgresDsn schemes. Example: `postgresql+asyncpg`

:warning: Make sure to setup the `.env` file because this will be necessary to start the application using docker

:warning: I highly suggest you use linux to deploy this app, if you are on windows make sure you are developing under [WSL2](https://docs.microsoft.com/pt-br/windows/wsl/install-win10)

## .env CONFIG

Before running the app, make sure to create a `.env` file on project root. All environment variables available are declared on on `settings.py`.

As this project uses pydantic BaseSettings, the `.env` file will populate the `Settings` class accordingly.

Below is a sample of how your `.env` file shall look.

```sh
GOOGLE_CLIENT_ID = #replace: google-client-id-here
GOOGLE_CLIENT_SECRET = #replace: google-client-secret-here
GOOGLE_REDIRECT_URL = http://localhost:8000/api/v1/login/google-login-callback/
GOOGLE_DISCOVERY_URL = https://accounts.google.com/.well-known/openid-configuration

SUPER_USER_NAME = admin
SUPER_USER_PASSWORD = admin
SUPER_USER_EMAIL = admin@example.com
SUPER_USER_BIRTHDATE = 1970-01-01

DATABASE_TYPE=postgresql
POSTGRES_USER = admin
POSTGRES_PASSWORD = admin
POSTGRES_DB = app
POSTGRES_SERVER = db # do not change this -> a change here requires a docker-compose change as well

REDIS_URI = redis://redis:6379 # do not change this -> a change here requires a docker-compose change as well
```

## Handling the Database

`ALEMBIC` is now being used to handle database migrations, so please make sure to use it instead of manually modifying the database.

After changing some database model, run `alembic revision --autogenerate -m "comment the model change here"` to create a new version file.
Make sure you commit this file to the repo.

Alembic migrations are run by the `scripts/prestart.sh` script when initializing the application via docker.

In case there is any doubt, go to [ALEMBIC Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) and check the instructions.

## Using docker-compose

To run this application, all you need to do is run the following command:

```sh
docker-compose up -d --build
```

This will start the following services:

- [Traefik](https://doc.traefik.io/traefik/) to serve as a reverse proxy for our application
- [Redis](https://redis.io/) to serve as a cache service for our application
- [Postgres](https://www.postgresql.org/) to serve as a database for our application
- This very api will also be started by docker under the service name of `web`

Hopefully :pray: , if everything worked as expected, you will be able to access the application on [Caishen User API](http://localhost:8000)
