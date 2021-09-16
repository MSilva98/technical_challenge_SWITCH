FROM python:3
ENV PYTHONUNBUFFERED=1
RUN apt-get update -y && apt-get install -y python-dev
WORKDIR /payments_app
COPY requirements.txt /payments_app/
RUN pip3 install -r requirements.txt
COPY ./payments_app/ /payments_app/