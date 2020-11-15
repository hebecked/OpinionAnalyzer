FROM grafana/grafana:7.1.5

USER root

ADD ./config.ini /etc/grafana/grafana.ini
ADD ./dashboards /var/lib/grafana/dashboards
ADD --chown=grafana ./provisioning /etc/grafana/provisioning
#ADD --chown=grafana ./plugins/ /var/lib/grafana/plugins/