FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y libpq-dev \
    && apt-get install -y gettext \
    && apt-get install -y gcc python3-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install sqlalchemy
RUN pip install pip install channels-redis==3.4.1
RUN pip install pip install channels==4.0.0
RUN #pip install pip install daphne==4.0.0
#RUN #pip install uvicorn
COPY entrypoint.sh /entrypoint
RUN chmod +x /entrypoint

COPY start.sh /start
RUN chmod +x /start

COPY worker-start.sh /start-celery-worker
RUN chmod +x /start-celery-worker

COPY beat-start.sh /start-celery-beat
RUN chmod +x /start-celery-beat
COPY media/img/avatar/ media/img/avatar/
COPY . .

ENTRYPOINT ["/entrypoint"]

