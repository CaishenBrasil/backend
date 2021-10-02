# Project Structure Overview

This is how the project is organized, directory wise.

## Project folders

```sh
.
├── api
├── cert
├── docs
├── logstash
├── scripts
└── traefik
```

The project code is located under the `api` folder. While the documentation is under the `docs` folder.

The `cert` folder contains local ssl certificates that help us develop locally with HTTPS enabled.

The `traefik` folder contains [Traefik](https://doc.traefik.io/traefik/) configuration files.

The `logstash` folder contains [Logstash](https://www.elastic.co/logstash/) configuration files.

The `scripts` folder contains scripts that are used to deploy our application.

## Understand the api folder organization

```sh
.
├── alembic
├── core
├── crud
├── dependencies
├── models
├── routers
├── schemas
└── utils
```

This project structure is greatly inspired by this basic [FastAPI Project Generator](https://github.com/tiangolo/full-stack-fastapi-postgresql).

Let's go ahead and check what each folder contains.

### Alembic

The `alembic` folder contains [alembic](https://alembic.sqlalchemy.org/en/latest/) related files, this folder was created using the `alembic init` command.

```sh
.
├── alembic
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
```

We had to make some adjustments to `env.py` to adapt it to our project settings, these will be later explained on Alembic own article.

### Core

The `core` folder contains, as you might guess, core functionality of our application.

```sh
.
├── core
│   ├── __init__.py
│   ├── exceptions
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   ├── authorization.py
│   │   ├── base.py
│   │   ├── cache.py
│   │   ├── database.py
│   │   └── handlers.py
│   ├── logging
│   │   ├── __init__.py
│   │   ├── caishen_logger.py
│   │   └── settings.py
│   ├── security.py
│   └── serializers.py
│   └── database.py
```

It holds configuration about our application exceptions, logging, security and serializers.

The `exceptions` folder contains not only exception class definitions, but also handlers that are later used in the `main.py` file as FastAPI exceptions handlers.

The `logging` folder has our default logger defined under `caishen_logger.py` but also all logging definition defined under `settings.py` which uses pydantic BaseSettings class to do some magic :smile:.

The `security` model defines only password hashing functionality, finally the serializers are there just so we can wrap orjson `dumps` method, so we can return a string instead of bytes as recommended on [pydantic documentation](https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation).

The `database` model defines the database Session which we use to connect and interact with the database.

### CRUD

CRUD stands for Create Read Update Delete, which are operations used in REST APIs. Those operations usually requires database connections.

It means that every database operation for each database we've configured are defined under this folder.

```sh
├── crud
│   ├── __init__.py
│   ├── base.py
│   └── user.py
```

Currently we have only one database table defined: `users`, so apart from the `base` CRUD from which every other CRUD inherits, only `user` CRUD is defined.

### Dependencies

Dependencies is where we define our FastAPI dependency injection.

!!! quote "FastAPI Dependency Injection"

    "Dependency Injection" means, in programming, that there is a way for your code (in this case, your path operation functions) to declare things that it requires to work and use: "dependencies".

    And then, that system (in this case FastAPI) will take care of doing whatever is needed to provide your code with those needed dependencies ("inject" the dependencies).

    This is very useful when you need to:

    - Have shared logic (the same code logic again and again).
    - Share database connections.
    - Enforce security, authentication, role requirements, etc.
    - And many other things...

    Reference: [FastAPI Dependencies Tutorial](https://fastapi.tiangolo.com/tutorial/dependencies/)

```sh
├── dependencies
│   ├── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── providers.py
│   │   ├── schemes.py
│   │   └── security.py
│   ├── cache.py
│   ├── database.py
│   └── user.py
```

In our case we have a few dependency injections needed.

- `cache` for getting a Redis connection.
- `database` for getting a PostgreSQL connection.
- `user` for getting the current user who is accessing our application.
- `auth` where we define all the magic needed to login with OAuth providers like Google and Facebook and also to login with our Local provider (which is not Oauth).

!!! note "Auth dependencies"

    This `auth` folder was previously under `core`, however as the majority of its classes and functions are used as dependencies I decided to move it to the  `dependencies` folder instead.

    This is a great example of arbitrary choices I've made in order to organize this project. You might have different ideas about it and implement it in a different structure, and that's okay.

    Also, notice that things might change overtime, so don't get stuck because you don't know exactly where a specific piece of code should go.

### Models

This is where all SQLAlchemy model classes are defined.

```sh
├── models
│   ├── __init__.py
│   ├── base.py
│   └── user.py
```

For now, only the `user` model is defined, which inherits from `base`.

### Schemas

This is where all Pydantic model classes are defined.

```sh
├── schemas
│   ├── __init__.py
│   ├── auth.py
│   ├── base.py
│   ├── logs.py
│   ├── token.py
│   └── user.py
```

Pydantic is used to (de)serialize data to and from our API.

The `user` file for example, has several `user` schemas defined. One for each different use cases we might have on our application. We have a UserRead, UserCreate, UserCreateLocal, and others.

There is also schemas for logs, auth and tokens. Those are better explained on their own articles.

### Routers

We don't want to specify every endpoint on a single file like `main.py`.

To better organize our project we make use of the APIRouter class from FastAPI which allows us to define endpoints (aka routes) in different modules and later import them to our application using the `include_router` method.

```sh
├── routers
│   ├── __init__.py
│   ├── login.py
│   └── users.py
```

We have two defined routers so far, one for user operations and another one for login operations.

### Utils

The `utils` folder is where we place code that we have no idea where else to place. :laughing:

```sh
└── utils
    ├── __init__.py
    ├── check_logstash_status.py
    └── init_db.py
```

Seriously, those are just helper functions, for example, we have a function to check when the logstash agent we use to ship logs to Redis is ready, so we can delay our application startup until them.

And the second function is to initialize our database with superuser so we can have admin privilege in our application before we start it.
