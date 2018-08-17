# docker build -t telminov/sonm-cdn-node-manager .
# docker push telminov/sonm-cdn-node-manager
FROM ubuntu:18.04

RUN apt-get clean && apt-get update && apt-get install -y \
    supervisor \
    python3-dev \
    python3-pip \
    npm


ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

ENV PYTHONUNBUFFERED 1

COPY . /opt/app
WORKDIR /opt/app

RUN cp project/local_settings.sample.py project/local_settings.py

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisor/prod.conf /etc/supervisor/conf.d/app.conf

EXPOSE 80
VOLUME /data/
VOLUME /conf/
VOLUME /static/
VOLUME /media/

CMD test "$(ls /conf/local_settings.py)" || cp project/local_settings.sample.py /conf/local_settings.py; \
    rm project/local_settings.py;  ln -s /conf/local_settings.py project/local_settings.py; \
    python3 ./manage.py migrate; \
    npm install; \
    python3 ./manage.py collectstatic --no-input; mv node_modules/ static/; mv static/* /static/; \
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf --nodaemon