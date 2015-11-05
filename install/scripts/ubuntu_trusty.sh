#!/bin/bash

set -e # Exit if error thrown, See man page, thee is exceptions !
export DEBIAN_FRONTEND="noninteractive"

function log {
  echo "###### TRACIM install: $1"
}

CURRENT_PATH=`pwd`

log "Install path is $CURRENT_PATH"

log "Install system dependencies"
sudo apt-get update
sudo apt-get install -y realpath python3 python-virtualenv python3-dev python-pip build-essential\
                        postgresql-server-dev-all libxml2-dev libxslt1-dev python-lxml\
                        postgresql postgresql-client\
                        git

log "Get tracim sources and setup it's virtual env"
git clone -b dev/install/scripts https://github.com/buxx/tracim.git # TODO: depot buxx
cd tracim
virtualenv -p /usr/bin/python3 tg2env
source tg2env/bin/activate

log "Install tracim dependencies"
cd tracim/ && python setup.py develop && cd -
pip install -r install/scripts/ubuntu_trusty_requirements.txt
./bin/tg2env-patch 1 tg2env/lib/python3.4/site-packages
./bin/tg2env-patch 2 tg2env/lib/python3.4/site-packages

log "Postgresql test database"
service postgresql start
sudo su postgres -c "psql -c 'create database tracim_test;' -U postgres"

log "Setup tracim"
cp tracim/development.ini.base tracim/development.ini
cd tracim && gearbox setup-app && cd -

# TODO: hors script (dans docker run)
log "Run tracim tests"
nosetests -c ${TRAVIS_BUILD_DIR}/tracim/test.ini -v
