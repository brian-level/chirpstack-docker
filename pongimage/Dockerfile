FROM alpine:3.9

RUN apk update
RUN apk add alpine-sdk
RUN apk add linux-headers
RUN apk add python3-dev
RUN apk add py3-pip
RUN pip3 install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN pip3 install wheel
RUN mkdir /usr/pong

COPY ./python/* /usr/pong

RUN pip3 install -r /usr/pong/requirements.txt


