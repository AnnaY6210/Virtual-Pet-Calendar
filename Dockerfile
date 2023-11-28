FROM python:3.10

COPY requirements.txt /app/requirements.txt
WORKDIR /app

# dependencies 
RUN pip install -r requirements.txt

COPY public/ /app
WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app