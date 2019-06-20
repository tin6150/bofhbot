FROM python:3.7-alpine

RUN apk add build-base
ADD . /bofhbot
WORKDIR /bofhbot
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/bofhbot/bofhbot.py" ]
