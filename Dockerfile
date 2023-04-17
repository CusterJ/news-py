FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install -y supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 9001 8888

CMD ["/usr/bin/supervisord"]