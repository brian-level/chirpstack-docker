FROM ubuntu

RUN apt update
RUN apt -y install inetutils-ping
RUN apt -y install python3
RUN apt -y install python3-pip
RUN pip3 install wheel
RUN pip3 install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN mkdir /usr/pong
COPY ./python/* /usr/pong
RUN pip3 install -r /usr/pong/requirements.txt


