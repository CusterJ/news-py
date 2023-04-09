
FROM python:alpine3.17

ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8888
# EXPOSE $PORT

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python", "$APP"]