FROM python:3.8-slim

ENV DEBIAN_FRONTEND=non-interactive
ENV PYTHONUNBUFFERED True


# Install necessary packages and Firefox
RUN apt-get update \
    && apt-get install -y --no-install-recommends firefox-esr wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install GeckoDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.33.0-linux64.tar.gz \
    && rm geckodriver-v0.33.0-linux64.tar.gz \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD uvicorn API:app --port=8000 --host=0.0.0.0