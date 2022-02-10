#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose --no-ansi"
DOCKER="/usr/bin/docker"

cd ~/56-kabinet/
$COMPOSE run certbot renew && $COMPOSE restart nginx
$DOCKER system prune -af