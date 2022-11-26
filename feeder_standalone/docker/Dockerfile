FROM python:3.8.15-alpine3.16

ADD ./feeder_standalone/docker/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
ENV FLASK_APP=/app/feeder.py
ADD ./feeder_standalone/docker/feeder.py /app/feeder.py
ADD ./feeder_standalone/docker/feeder_test.py /app/feeder_test.py

ENTRYPOINT ["/usr/local/bin/flask", "run", "--host=0.0.0.0", "--port=80"]