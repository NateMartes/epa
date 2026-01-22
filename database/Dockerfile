FROM python:3.11-slim

COPY init.py /
COPY config.json /
COPY requirements.txt /

RUN pip install -r requirements.txt

CMD ["python3","init.py"]
