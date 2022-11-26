FROM python:3.8.15-alpine3.16

ADD requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
ENV FLASK_APP=/app/manager.py
ADD manager.py /app/manager.py
ADD manager_test.py /app/manager_test.py

ENTRYPOINT ["/usr/local/bin/flask", "run", "--host=0.0.0.0", "--port=80"]