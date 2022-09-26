FROM python:3.9

ADD ./src/*.py /opt/app/
COPY access.log /var/log
WORKDIR /opt/app
ENTRYPOINT python3 /opt/app/log_analyze.py
