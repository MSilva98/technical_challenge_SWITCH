FROM python:3
ENV PYTHONUNBUFFERED=1
RUN apt-get update -y && apt-get install -y python-dev
WORKDIR /refunds_app
COPY requirements.txt /refunds_app/
RUN pip3 install -r requirements.txt
COPY ./refunds_app/ /refunds_app/
