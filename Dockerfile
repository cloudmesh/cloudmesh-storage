FROM ubuntu:19.04

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install git
RUN apt-get -y install curl


RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN pip install cloudmesh-installer
RUN mkdir cm

WORKDIR cm

RUN cloudmesh-installer git clone storage
RUN cloudmesh-installer install storage -e

# RUN cms help


