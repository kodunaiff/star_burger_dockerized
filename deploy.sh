#!/bin/bash
cd /opt/star_burger_dockerized/
docker compose -f docker-compose.prod.yml down
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear




echo Finished!