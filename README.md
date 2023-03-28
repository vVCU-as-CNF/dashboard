# it2s-grafana-dashboard
This repository provides a docker stack to display info from virtual ITS station digital twins, via MQTT broker.

## Architeture
This stack implements the services contained in green on the following image:

![architecture](./doc/architecture.png)

## Notes
* MQTT payloads are always expected to be in JSON format;
* MQTT payloads from the digital twins are published at 'obu/inqueue/json/`<`stationID`>`/`<`messageType`>`';
* The proxy currently exists only to parse the perceived objects contained in CPMs;
* A template is provided in 'grafana/template.json' that can be imported to a functional dashboard;
* Environment variables can be set directly in the grafana container to install specific plugins on start:
```
docker run -d -p 3000:3000 --name=grafana -e "GF_INSTALL_PLUGINS=grafana-mqtt-datasource" grafana/grafana-enterprise
```
* Topics currently used in the dashboard provided by the template:
```
# Used to get information directly from CAMs:
obu/inqueue/json/<stationID>/CAM
# Used to get information directly from CPMs:
obu/inqueue/json/<stationID>/CPM
# Used to get information parsed from the CPMs (through the proxy):
obu/outqueue/json/<stationID>/perceivedObjects
# Used to get the staiton's 5G module access level info:
logs/access
```

## TODO
* Choose better MQTT topics structure, mostly from access logs.
* The proxy currently has the MQTT server host hard coded. This should be set as an environment variable of the container;
* The template should be extended with additional functionalities/dashboards once the digital twin's orchestrator exists, such as:
    * Which ITS stations are virtualized in each MEC platform;
    * Network level latencies;
    * Application level lantecies.