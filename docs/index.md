# About this Project

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/CaishenBrasil/caishen-user-api/dev.svg)](https://results.pre-commit.ci/latest/github/CaishenBrasil/caishen-user-api/dev)

This project goal is simple: Learn REST API development by developing one.

This is a personal project that I've came up with to learn a little bit of web development, backend engineering and overall best practices.

While developing, there are several doubts that comes up along the way, this documentation aims to address those once solved doubts, so that others that might have questions similar to those I had may benefit from this project to learn as I have learned while building it.

My goal with this documentation is to write a blog about web development, and relate to code I've written here so anyone can clone the repo, start the server on their own machine and experiment. Think of it as a hands-on lab of a REST API backend application.

Contributions to the project are **very welcomed**, as long as you want to also write documentation for the code you're pushing, so everyone can follow along.

Contribute to the code: [Caishen Backend](https://github.com/CaishenBrasil/backend)

## Project Dependencies

I'll list each dependency we use in this project, right here in this section. Some dependencies might have an exclusive document used to explain why and how we use it in this project, so stay tuned for updates!

### Main Dependencies

[Python](https://www.python.org/) - The BEST programming language ever!

[Poetry](https://python-poetry.org/) - THE python packaging and dependency manager that pip should be :wink:

This project wouldn't exist if it weren't for [FastAPI](https://fastapi.tiangolo.com/), a python Web Framework for building APIs. FastAPI is the backbone of the project.

As we rely on FastAPI, [Pydantic](https://pydantic-docs.helpmanual.io/) also plays a huge role on the project. By the way, Pydantic might be my favorite python library ever.

[SQLAlchemy](https://www.sqlalchemy.org/) is also another dependency, the go-to python ORM for talking to SQL databases. We're already using SQLAlchemy 2.0 dialect to make things *future proof*.

There are, of course, other dependencies, but they are not as important as those I've just mentioned, nonetheless, I will explain them below:

- [Uvicorn](https://www.uvicorn.org/) is a python ASGI web server that runs FastAPI code.
- [alembic](https://alembic.sqlalchemy.org/en/latest/) is a database migration tool to use together with SQLAlchemy.
- [passlib](https://passlib.readthedocs.io/en/stable/) is a password hashing library that we use not only to hash passwords but also to create random words to be used as CSRFTokens.
- [python-jose](https://python-jose.readthedocs.io/en/latest/) is an implementation of the JavaScript Object Signing and Encryption (JOSE) technologies, we use it to handle JSON Web Tokens.
- [aioredis](https://aioredis.readthedocs.io/en/latest/) is an async [Redis](https://redis.io/) client that we use to handle our Redis cache which is used to store tokens and as a queue for logs as well.
- [asyncpg](https://magicstack.github.io/asyncpg/current/) is the PostgreSQL async client we use.
- [structlog](https://www.structlog.org/en/stable/) is our logging library, we use this to convert our logs to JSON format so we can handle them easier in the ELK stack.
- [orjson](https://github.com/ijl/orjson) is the JSON (de)serializer library we use together with pydantic and structlog to handle JSON (de)serialization.
- [httpx](https://www.python-httpx.org/) the async http request library that we use to make http requests towards other services from within our application.

### Development Dependencies

Development dependencies are those used only while developing, on this app, we mainly use code quality and documentation dependencies.

A huge thanks to [pre-commit](https://pre-commit.com/) which makes code quality assurance much easier. With it we can easily handle git hooks, mostly, pre-commit hooks so we can guarantee code quality is maintained across different contributors. If the pre-commit hook fails, code is not even committed. :smile:

Another incredible dependency is [black](https://black.readthedocs.io/en/stable/) which can automatically format code for us, so we don't lose time fixing minor formatting issues. Use black and [flake8](https://flake8.pycqa.org/en/latest/) and have formatting issues just disappear from your code!

Last, but not least (at all!) [mypy](http://mypy-lang.org/) the static type checker that makes hard to catch bugs, easy to solve.

??? note "A note on type annotations"
    I though static typing python code was a waste of time, however with editor support and mypy, productivity with static typing is just **incredible** and the kind of bugs that we avoid by just using such a simple tool like that is worth it.

    Please, use typing in your projects!
