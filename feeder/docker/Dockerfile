FROM python:3.8.15-buster

# Add PIP Requirements file and installing them
ADD ./feeder/docker/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Add python application files
ADD ./feeder/docker/feeder.py /app/feeder.py
ADD ./feeder/docker/feeder_test.py /app/feeder_test.py

ENTRYPOINT ["/usr/local/bin/python3", "-u", "/app/feeder.py"]