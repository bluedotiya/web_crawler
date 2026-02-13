FROM python:3.11-slim-bookworm

# Install nslookup
RUN DEBIAN_FRONTEND=noninteractive apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install dnsutils -y

# Add PIP Requirements file and installing them
ADD requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Add python application files
ADD feeder.py /app/feeder.py
ADD feeder_test.py /app/feeder_test.py

ENTRYPOINT ["/usr/local/bin/python3", "-u", "/app/feeder.py"]