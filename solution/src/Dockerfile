FROM python:3

ENV PYTHONUNBUFFERED 1

ENV TZ America/Sao_Paulo

ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8

RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /app

WORKDIR /app

ADD requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt
