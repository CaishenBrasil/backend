
echo "Waiting for postgres connection"

while ! nc -z db 5432; do
    sleep 0.1
done

echo "Run database migrations with alembic upgrade head"
alembic upgrade head

echo "PostgreSQL started"

echo "Waiting for Redis to be ready"
while ! nc -z redis 6379; do
    sleep 0.1
done

echo "Redis Cache is UP, checking logstash agent"

echo "Wait for logstash agent service to be up"

while : ; do
    logstash=$(python api/utils/check_logstash_status.py)
    if [ $logstash = "1" ]
        then
            echo "Logstash Agent is UP"
            break
    fi
    sleep 0.5
done

echo "Run init_db.py to populate DB"
python api/utils/init_db.py

exec "$@"
