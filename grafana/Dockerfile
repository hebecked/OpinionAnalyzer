FROM grafana/grafana:7.4.3

USER root

ADD ./config.ini /etc/grafana/grafana.ini
ADD ./dashboards /var/lib/grafana/dashboards
ADD ./provisioning /etc/grafana/provisioning
