FROM python:3.8.6-buster

ENV PYTHONUNBUFFERED 1


WORKDIR /code

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /code

EXPOSE 8050


CMD ["python", "./main.py"]
