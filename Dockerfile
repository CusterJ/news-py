FROM python:slim-bullseye

RUN apt-get update && \
    apt-get install -y supervisor && \
    mkdir -p /var/log/supervisor

# COPY requirements.txt /app
COPY . /app

# RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 9001
EXPOSE 8888

CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]