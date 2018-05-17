FROM ubuntu:18.04
EXPOSE 80

RUN apt-get clean && apt-get update && apt-get install -y \
    supervisor \
    python3-dev \
    python3-pip


ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

ENV PYTHONUNBUFFERED 1

COPY . /opt/app
WORKDIR /opt/app

RUN cp project/local_settings.sample.py project/local_settings.py

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisor/prod.conf /etc/supervisor/conf.d/app.conf

CMD test "$(ls /conf/local_settings.py)" || cp project/local_settings.sample.py /conf/local_settings.py; \
    rm project/local_settings.py;  ln -s /conf/local_settings.py project/local_settings.py; \
    python3 ./manage.py migrate; \
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf --nodaemon