FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

EXPOSE 8080

WORKDIR /app

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "stTweetoxicity.py", "--server.port=8080", "--server.address=0.0.0.0"]