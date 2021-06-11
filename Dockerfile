FROM pandoc/ubuntu-latex:2.14.0.1

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip
ADD requirements.txt /app
RUN pip3 install -r requirements.txt

ADD . /app

ENTRYPOINT []
CMD ["/app/run.sh"]