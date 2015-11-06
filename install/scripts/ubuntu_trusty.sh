#!/bin/bash

<<'COMMENT'
Install script for tracim on Ubuntu Trusty:
To test it in test script (like travis-ci) with docker,
run (assuming you are in tracim repository folder):

docker run -i ubuntu:14.04 /bin/bash -c \
    'cat > /install.sh && /bin/bash /install.sh \
    && cd /tracim/tracim && /tracim/tg2env/bin/nosetests -c tracim/test.ini \
    < ./install/scripts/ubuntu_trusty.sh

where ./install/scripts/ubuntu_trusty.sh is this script.
COMMENT

#
# START CONFIGURATION
#

GITHUB_REPO="https://github.com/buxx/tracim.git" # TODO: depôt final tracim/tracim
TRACIM_TEST_DB_NAME="tracim_test"
TRACIM_TEST_USER_LOGIN="postgres"
TRACIM_TEST_USER_PASS="dummy"

#
# END CONFIGURATION
#

function log {
  echo "###### TRACIM INSTALL: $1"
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
git clone -b dev/install/scripts $GITHUB_REPO
cd tracim
virtualenv -p /usr/bin/python3 tg2env
source tg2env/bin/activate

log "Install tracim dependencies"
cd tracim/ && python setup.py develop && cd -
pip install -r install/scripts/ubuntu_trusty_requirements.txt
./bin/tg2env-patch 1 tg2env/lib/python3.4/site-packages
./bin/tg2env-patch 2 tg2env/lib/python3.4/site-packages

log "Postgresql test database"
sudo service postgresql start
sudo -u postgres psql -U postgres -c "create database $TRACIM_TEST_DB_NAME;"
sudo -u postgres psql -U postgres -c "alter user $TRACIM_TEST_USER_LOGIN with password '$TRACIM_TEST_USER_PASS';"

log "Setup tracim"
cp tracim/development.ini.base tracim/development.ini
cd tracim && gearbox setup-app && cd -
