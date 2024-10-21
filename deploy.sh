#!/bin/bash
cd /opt/star_burger_dockerized/
docker compose -f docker-compose.prod.yml down
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

if [ -e ".env" ]; then
    source .env
fi

GIT_HASH=$(git rev-parse --short HEAD)

if [ -v ROLLBAR_TOKEN ]; then
   curl -H "X-Rollbar-Access-Token: ${ROLLBAR_TOKEN}" \
        -H "Content-Type: application/json" \
        -X POST 'https://api.rollbar.com/api/1/deploy' \
        -d "{\"environment\": \"production\", \"revision\": \"${GIT_HASH}\", \
        \"rollbar_name\": \"Kodu\", \"local_username\": \"$(whoami)\", \
        \"comment\": \"deployment\", \"status\": \"succeeded\"}"
   echo "Sended log to LOGBAR"
fi


echo Finished!