FROM python:3.9-bullseye

ENV PYTHONBUFFERED=1

WORKDIR /NDC_user_docker

COPY requirements.txt requirements.txt

# Set pip default timeout
ENV PIP_DEFAULT_TIMEOUT=500

RUN pip3 install --no-cache-dir -r requirements.txt


COPY . .

CMD gunicorn NDC_local.wsgi:application --bind 0.0.0.0:8001

EXPOSE 8001