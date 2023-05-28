#/usr/bin/bash
docker network remove grafana
docker network create grafana
docker run --rm -d -p 1883:1883 --network grafana -v ./mosquitto.conf:/mosquitto/config/mosquitto.conf --name mosquitto eclipse-mosquitto
