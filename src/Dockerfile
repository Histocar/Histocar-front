FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

RUN apt-get update && apt-get install -y xvfb

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN playwright install

COPY . .

RUN apt-get install -y flac ffmpeg

ENV PYTHONPATH="/app"

CMD ["sh", "-c", "xvfb-run --auto-servernum --server-args='-screen 0 1920x1080x24' gunicorn -w 2 -b 0.0.0.0:8080 --timeout 120 informe:app"]
