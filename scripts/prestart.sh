
echo "Waiting for postgres connection"

while ! nc -z db 5432; do
    sleep 0.1
done

echo "Run database migrations with alembic upgrade head"
alembic upgrade head

echo "PostgreSQL started"

exec "$@"
