FROM python:3.9-bullseye

ENV PYTHONBUFFERED=1

WORKDIR /NDC_manager_docker

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD gunicorn NDC_manager.wsgi:application --bind 0.0.0.0:8000

EXPOSE 8000