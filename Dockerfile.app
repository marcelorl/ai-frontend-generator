FROM python:3.11-slim

WORKDIR /workspaces

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U pip
RUN pip3 install --no-cache -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

COPY ./app ./app
COPY ./results ./results

WORKDIR /workspaces/app

CMD ["streamlit", "run", "app.py"]
