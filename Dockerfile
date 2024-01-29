FROM python:3.8-slim

WORKDIR /usr/src/endege

COPY app app
COPY config config
COPY nginx_conf_back nginx_conf_back
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6482

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:6482", "app.main:app"]


