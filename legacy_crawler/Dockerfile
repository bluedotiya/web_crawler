FROM python:3.8.15-alpine3.16

# Install Matplotlibe requirements
RUN apk add g++ jpeg-dev zlib-dev libjpeg make

# Addding python pip requirements fiile
ADD legacy_crawler/docker/requirements.txt /app/requirements.txt

# Pip installing all required packages
RUN pip3 install -r /app/requirements.txt --use-deprecated=backtrack-on-build-failures

# Added the rest of application files
ADD legacy_crawler/docker /app 

# Change Workdir to /app and create output folder
WORKDIR /app

ENTRYPOINT ["/usr/local/bin/python3", "-u", "/app/Webigator.py"]