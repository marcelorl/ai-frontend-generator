FROM python:3.11-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U pip
RUN pip3 install --no-cache -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

WORKDIR /workspaces
