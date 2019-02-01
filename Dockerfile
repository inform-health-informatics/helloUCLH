FROM jupyter/demo
USER root
RUN mkdir /code 
WORKDIR /code
USER $NB_USER
