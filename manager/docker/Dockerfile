FROM python:3.8.15-buster

# Add PIP Requirements file and installing them
ADD ./manager/docker/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Set FLASK application path
ENV FLASK_APP=/app/manager.py

# Add python application files
ADD ./manager/docker/manager.py /app/manager.py
ADD ./manager/docker/manager_test.py /app/manager_test.py
ADD ./manager/docker/index.html /app/index.html

ENTRYPOINT ["/usr/local/bin/flask", "run", "--host=0.0.0.0", "--port=80"]