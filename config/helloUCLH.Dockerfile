# Adapted from
# https://hub.docker.com/r/leandatascience/jupyterlabconfiguration
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential  \
     checkinstall \
     libreadline-gplv2-dev \
    libncursesw5-dev \
    libssl-dev \
    libsqlite3-dev \
    tk-dev \
    libgdbm-dev \
    libc6-dev \
    libbz2-dev \
    zlib1g-dev \
    openssl \
    libffi-dev \
    python3-dev \
    python3-setuptools \
    wget


RUN mkdir /tmp/Python37 \
    && cd /tmp/Python37 \
    && wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz \
    && tar xvf Python-3.7.0.tar.xz \
    && cd /tmp/Python37/Python-3.7.0 \
    && ./configure \
    && make altinstall

RUN ln -s /usr/local/bin/python3.7 /usr/bin/python
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py

RUN pip install --upgrade pip
RUN pip install requests
RUN apt-get install curl -y

RUN pip install jupyter --upgrade
RUN pip install jupyterlab --upgrade

RUN apt-get install pandoc -y
RUN apt-get install texlive-xetex -y

RUN unlink /usr/bin/python
RUN ln -s /usr/local/bin/python3.7 /usr/bin/python

RUN apt-get install bash -y
RUN pip install bash_kernel
RUN python -m bash_kernel.install

# 2019-02-02
# Install postgres to permit installation of psycopg2
# https://stackoverflow.com/a/12037133
RUN apt-get install libpq5
#####

# see above : installed separately so no dependency on the source
# FROM leandatascience/configcredential
ENV MAIN_PATH=/usr/local/bin/helloUCLH
ENV LIBS_PATH=${MAIN_PATH}/libs
ENV CONFIG_PATH=${MAIN_PATH}/config
ENV NOTEBOOK_PATH=${MAIN_PATH}/notebooks

RUN pip install -U pandas numpy scipy matplotlib altair
RUN pip install -U sqlalchemy psycopg2

EXPOSE 8889

CMD cd ${MAIN_PATH} && sh config/run_jupyter.sh
