FROM python:3.8.15-alpine3.16

ADD feeder.py /app/feeder.py
ADD requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
ENV FLASK_APP=/app/feeder.py

ENTRYPOINT ["/usr/local/bin/flask", "run", "--host=0.0.0.0", "--port=80"]