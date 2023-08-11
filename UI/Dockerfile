FROM python:3.8

ENV PYTHONUNBUFFERED True

EXPOSE 8080

WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "stTweetoxicity.py", "--server.port=8080", "--server.address=0.0.0.0"]