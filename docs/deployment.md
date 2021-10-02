# Deployment

!!! warning "Set an .env file"
    Make sure to setup the `.env` file because this will be necessary to start the application using docker

!!! tip "Development environment"
    I highly suggest you use linux to deploy this app, if you are on windows make sure you are developing under [WSL2](https://docs.microsoft.com/pt-br/windows/wsl/install-win10)

## Environment Variables

Before running the app, make sure to create a `.env` file on project root. All environment variables available are declared on on `settings.py`.

As this project uses pydantic BaseSettings, the `.env` file will populate the `Settings` class accordingly.

Below is a sample of how your `.env` file shall look.

### Caishen Enviroment Variables

```ini
DEV = False
LOG_LEVEL = DEBUG

GOOGLE_CLIENT_ID = #replace: google-client-id-here
GOOGLE_CLIENT_SECRET = #replace: google-client-secret-here
GOOGLE_REDIRECT_URL = http://localhost:8000/api/v1/login/google-login-callback/
GOOGLE_DISCOVERY_URL = https://accounts.google.com/.well-known/openid-configuration

FACEBOOK_CLIENT_ID = #replace: facebook-app-id-here
FACEBOOK_CLIENT_SECRET = #replace: facebook-app-secret-here
FACEBOOK_REDIRECT_URL = https://localhost/api/v1/login/facebook-login-callback
FACEBOOK_DISCOVERY_URL = https://www.facebook.com/.well-known/openid-configuration/
FACEBOOK_AUTHORIZATION_ENDPOINT = https://facebook.com/dialog/oauth/
FACEBOOK_TOKEN_ENDPOINT = https://graph.facebook.com/oauth/access_token
FACEBOOK_USERINFO_ENDPOINT = https://graph.facebook.com/me

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

### Gunicorn Environment Variables

To maintain consistency, we've re-written gunicorn config file  in `gunicorn_config.py` and used pydantic BaseSettings class to read environment variables for gunicorn.
As a result, you can pass those variables by creating a file called `gunicorn.env`, check an example below:

```sh
WORKERS_PER_CORE = 1.0
HOST = 0.0.0.0
PORT = 80
LOG_LEVEL = INFO
GRACEFUL_TIMEOUT = 120
TIMEOUT = 120
KEEP_ALIVE = 5
```

## Handling the Database

`ALEMBIC` is now being used to handle database migrations, so please make sure to use it instead of manually modifying the database.

After changing some database model, run `alembic revision --autogenerate -m "comment the model change here"` to create a new version file.
Make sure you commit this file to the repo.

Alembic migrations are run by the `scripts/prestart.sh` script when initializing the application via docker.

In case there is any doubt, go to [ALEMBIC Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) and check the instructions.

## Using HTTPS Locally

It's always great to have our development environment as close as the production environment for testing purposes.

So, developing with HTTPS locally is encouraged. Traefik makes it very easy to do that, even when using localhost. Here is a step by step on how to create your own certificates.
This step by step was pretty much copied from [Freecodecamp](https://www.freecodecamp.org/news/how-to-get-https-working-on-your-local-development-environment-in-5-minutes-7af615770eec/).

### Step 1 - Generate a Root SSL Certificate

Generate a RSA-2048 key and save it to a file rootCA.key. This file will be used as the key to generate the Root SSL certificate. You will be prompted for a pass phrase which you’ll need to enter each time you use this particular key to generate a certificate.

`openssl genrsa -des3 -out rootCA.key 2048`

`openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.pem`

### Step 2 - Add the certificate to trusted certificate on your machine

You might need to search on how to do it on your machine, I'll briefly explain it here for Windows OS.

- Search for `certificates` on Windows and open the Certificates Manager.
- Open up the folder where it says Trusted Root Certificates, or something similar to it.
- Open up the certificates folder.
- Right click on the right window, go to "All Tasks" --> Import.
- Finally, import the rootCA.pem we've just created. If this is not showing up, just select "Show all files" and select the *.pem file.

### Step 3 - Domain SSL certificate

The root SSL certificate can now be used to issue a certificate specifically for your local development environment located at localhost.

Create a new OpenSSL configuration file server.csr.cnf so you can import these settings when creating a certificate instead of entering them on the command line.

```ini
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn

[dn]
C=US
ST=RandomState
L=RandomCity
O=RandomOrganization
OU=RandomOrganizationUnit
emailAddress=hello@example.com
CN = localhost
```

Create a v3.ext file in order to create a X509 v3 certificate. Notice how we’re specifying subjectAltName here.

```ini
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
```

Create a certificate key for localhost using the configuration settings stored in server.csr.cnf. This key is stored in server.key.

`openssl req -new -sha256 -nodes -out server.csr -newkey rsa:2048 -keyout server.key -config <( cat server.csr.cnf )`

A certificate signing request is issued via the root SSL certificate we created earlier to create a domain certificate for localhost. The output is a certificate file called server.crt.

`openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 500 -sha256 -extfile v3.ext`

### Step 4 - Import them to traefik

Finally, we can use our generated certificate and key (server.key and server.crt) to encrypt our HTTP connection using Traefik.

On the docker-compose file under the Traefik service, there is a list of volumes defined:

```yml
        volumes:
            - ...
            - ./cert/server:/etc/certs:ro
            - ...
            - ...
```

Make sure the certificate `server.crt` and the key `server.key` are referenced to the container on `/etc/certs:ro`.

On the example above both the certificate and the key are stored under `/cert/server` on my local machine. You can store them on this path as well  to make your life easier.

## Using docker-compose

To run this application, all you need to do is run the following command:

```sh
docker-compose up -d --build
```

This will start the following services:

- [Traefik](https://doc.traefik.io/traefik/) to serve as a reverse proxy for our application
- [Redis](https://redis.io/) to serve as a cache service for our application
- [Postgres](https://www.postgresql.org/) to serve as a database for our application
- [ELK](https://www.elastic.co/) -> there are two services using logstash, one serves as an agent that receives logs from the docker GELF driver and send them to Redis, the other one acts as a consumer that fetches those logs from Redis and send them to elasticsearch. Finally, we use Kibana to visualize our logs.
- This very api will also be started by docker under the service name of `web`

Hopefully :pray: , if everything worked as expected, you will be able to access the application on [Caishen User API](https://localhost/api/v1)
