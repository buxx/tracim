FROM debian:jessie

# Disable frontend for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# All deb required packages
RUN apt-get update \
    && apt-get install -y realpath \
                          python3 \
                          python-virtualenv \
                          python3-dev \
                          python-pip \
                          build-essential \
                          postgresql-server-dev-all \
                          libxml2-dev \
                          libxslt1-dev \
                          python-lxml \
                          postgresql \
                          postgresql-client \
                          git

RUN git clone -b dev/deployment/docker https://github.com/buxx/tracim.git /tracim && echo 'foo'
RUN virtualenv -p /usr/bin/python3 /tracim/tg2env
RUN . /tracim/tg2env/bin/activate
RUN . /tracim/tg2env/bin/activate && cd /tracim/tracim && python setup.py develop
RUN . /tracim/tg2env/bin/activate && pip install -r /tracim/install/requirements.txt
RUN . /tracim/tg2env/bin/activate && SITE_PACKAGES_PATH=`python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"` \
    && /tracim/bin/tg2env-patch 1 $SITE_PACKAGES_PATH \
    && /tracim/bin/tg2env-patch 2 $SITE_PACKAGES_PATH
RUN cp /tracim/tracim/development.ini.base /tracim/tracim/development.ini


RUN service postgresql start \
    && su - postgres -c 'psql -U postgres -c "create database tracim_test;"' \
    && su - postgres -c "psql -U postgres -c \"alter user postgres with password 'dummy';\"" \
    && cd /tracim/tracim \
    && . /tracim/tg2env/bin/activate && gearbox setup-app

# Expose HTTP port
EXPOSE 8080

#
CMD ["/tracim/bin/run.sh"]
