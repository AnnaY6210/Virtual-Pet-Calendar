FROM python:3.10

# dependencies
RUN pip install Flask gunicorn firebase_admin

COPY public/ app/
WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app