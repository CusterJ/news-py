
FROM python:alpine3.17

ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8090

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# CMD ["python", "worker.py", "&"]
CMD ["python", "app.py"]
# CMD ["sh", "-c", "python app.py & python news_parser.py"]
