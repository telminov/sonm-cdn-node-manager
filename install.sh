#!/bin/sh
# /bin/sh install.sh -a "INSTANCE_HOST_IP" -p NODE_EXPOSE_PORT -u NODE_UPLOAD -d NODE_DOWNLOAD -k "key_store_path" -s "cli_yml_path" -c "CMS_URL" -t "COUNTERPARTY"

ERROR='\033[0;31m'
INFO='\033[1;34m'
NC='\033[m'
SUCCESS='\033[0;32m'

INSTANCE_HOST_IP=''
cli_yml_path='~/.sonm/cli.yaml'
key_store_path='/etc/sonm/sonm-keystore'
NODE_DOWNLOAD=50
NODE_UPLOAD=50
NODE_EXPOSE_PORT=80
COUNTERPARTY=""
CMS_URL=""
CHECK_SONM_CLI=false

function check_error {
    if [ $? -ne 0 ]; then
      echo "${ERROR}ERROR";
        exit 1
      else
        echo "${SUCCESS}SUCCESS";
    fi
}

while getopts ":a:p:u:d:k:s:p:c:t:f:" opt; do
  case $opt in
    a) INSTANCE_HOST_IP="$OPTARG"
    ;;
    p) NODE_EXPOSE_PORT="$OPTARG"
    ;;
    u) NODE_UPLOAD="$OPTARG"
    ;;
    d) NODE_DOWNLOAD="$OPTARG"
    ;;
    k) key_store_path="$OPTARG"
    ;;
    s) cli_yml_path="$OPTARG"
    ;;
    c) CMS_URL="$OPTARG"
    ;;
    t) COUNTERPARTY="$OPTARG"
    ;;
    f) CHECK_SONM_CLI=true
    ;;
    \?) echo "${ERROR}ERROR: ${NC}Invalid option -$OPTARG"; exit 1
    ;;
  esac
done

if [[ $INSTANCE_HOST_IP = "" ]]; then
   echo "${ERROR}ERROR: ${NC}Parameter INSTANCE_HOST_IP \"-a\" has been not empty";
   exit 1
fi

if [[ $CMS_URL = "" && ! CHECK_SONM_CLI ]]; then
   echo "${ERROR}ERROR: ${NC}Parameter CMS_URL \"-c\" has been not empty";
   exit 1
fi

echo "== INSTALATION SONM CDN NODE_MANAGER =="
echo "INSTANCE_HOST_IP:    " $INSTANCE_HOST_IP

if [ $CHECK_SONM_CLI = true ]; then
    echo "CHECK_SONM_CLI:      " $CHECK_SONM_CLI
else
    echo "NODE_EXPOSE_PORT:    " $NODE_EXPOSE_PORT
    echo "cli_yml_path:        " $cli_yml_path
    echo "key_store_path:      " $key_store_path
    echo "NODE_DOWNLOAD:       " $NODE_DOWNLOAD
    echo "NODE_UPLOAD:         " $NODE_UPLOAD
    echo "COUNTERPARTY:        " $COUNTERPARTY
    echo "CMS_URL:             " $CMS_URL
fi


echo "\n${INFO}Install python for remote host ... ${NC}"
ssh root@$INSTANCE_HOST_IP apt-get install -y python
check_error

if [ -d "./venv" ]; then
    echo "\n${INFO}Set virtual environment (venv) ...${NC}"
    source ./venv/bin/activate
    check_error
else
  echo "\n${INFO}Create virtual environment for ansible ... ${NC}"
  virtualenv venv
  check_error

  echo "\n${INFO}Set virtual environment (venv) ...${NC}"
  source ./venv/bin/activate
  check_error

  echo "\n${INFO}Install pip for current system ...${NC}"
  curl https://bootstrap.pypa.io/get-pip.py | python
  check_error
fi

echo "\n${INFO}Install ansible from ansible/requirements.txt ...${NC}"
pip install -r ansible/requirements.txt
check_error

echo "\n${INFO}Set INSTANCE_HOST_IP to ansible/inventory file ...${NC}"
echo "$INSTANCE_HOST_IP" > ansible/inventory
echo "${SUCCESS}SUCCESS";


if [ $CHECK_SONM_CLI = true ]; then
    echo "\n${INFO}Run ansible playbook for check sonmcli (ansible/intsall.yml)...${NC}"
    ansible-playbook -i ansible/inventory -u root ansible/install.yml --start-at-task='Check sonmcli'
    check_error
else
    echo "\n${INFO}Run ansible playbook (ansible/intsall.yml)...${NC}"
    ansible-playbook -i ansible/inventory -u root ansible/install.yml -e "cli_yml_path=$cli_yml_path key_store_path=$key_store_path CMS_URL=$CMS_URL COUNTERPARTY=$COUNTERPARTY NODE_DOWNLOAD=$NODE_DOWNLOAD NODE_UPLOAD=$NODE_UPLOAD NODE_EXPOSE_PORT=$NODE_EXPOSE_PORT"
    check_error
fi