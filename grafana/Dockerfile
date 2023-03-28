FROM grafana/grafana-enterprise

ENV GF_INSTALL_PLUGINS=grafana-mqtt-datasource
COPY ./grafana.ini /etc/grafana/grafana.ini
EXPOSE 3000

CMD ["grafana-server"]