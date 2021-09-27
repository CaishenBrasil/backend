
echo "Waiting for postgres connection"

while ! nc -z db 5432; do
    sleep 0.1
done

echo "Run database migrations with alembic upgrade head"
alembic upgrade head

echo "PostgreSQL started"

echo "Wait for logstash service to be up"
while ! nc -z -u logstash_agent 12201; do
    sleep 0.1
done

echo "Logstash Agent is UP, initializing FastAPI service"

exec "$@"
