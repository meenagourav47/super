FROM python:3.6-alpine

WORKDIR /app
COPY ./requirements.txt /app

RUN apk --no-cache --virtual=.build-deps add build-base musl-dev git &&\
    pip install --no-cache-dir -r requirements.txt &&\
    apk --purge del .build-deps

COPY . /app

RUN pip install -e .

ENV PYTHONUNBUFFERED=1
VOLUME /data
CMD python -m super.run
LABEL name=super version=dev
