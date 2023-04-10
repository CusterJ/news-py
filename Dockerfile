FROM python:slim-bullseye

COPY . /app

RUN apt-get update && \
    apt-get install -y supervisor && \
    pip install -r /app/requirements.txt && \
    mkdir -p /var/log/supervisor

EXPOSE 8888

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]