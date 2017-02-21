FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN apt-get update ; apt-get -y install mysql-client; apt-get clean
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
COPY ./docker-entrypoint.sh /
EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]
