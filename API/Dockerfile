FROM python:3.10-slim

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
RUN apt-get update && apt-get install -y git

RUN wget https://github.com/git-lfs/git-lfs/releases/download/v3.2.0/git-lfs-linux-amd64-v3.2.0.tar.gz && \
    tar -xzf git-lfs-linux-amd64-v3.2.0.tar.gz && \
    mv git-lfs-3.2.0/git-lfs /usr/local/bin/ && \
    rm -rf git-lfs-3.2.0 git-lfs-linux-amd64-v3.2.0.tar.gz

# Install Git LFS
RUN git lfs install

# Verify Git LFS installation
RUN git lfs version

RUN git clone https://huggingface.co/fathurfrs/indonesia-distilledbert-sentiment-classification /app/indonesia-distilledbert-sentiment-classification

CMD uvicorn API:app --port=8000 --host=0.0.0.0