# node-manger
Управление сетью хостов, на которые будет разворачиваться узлы CDN. 

Этот элемент должнен:
 - развернуть начальную сеть во всех регионах через SONM
 - следить за нагрузкой (например через prometeus) и по необходимости опускать/поднимать новые хосты


## Installation
Install example on Digital Ocean instance with Ubuntu Server 18.04

install python on host
```
ssh root@INSTANCE_HOST_IP
apt install -y python
```

start install ansible-playbook
```
cd <project_path>/ansible
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
echo "INSTANCE_HOST_IP" > inventory

ansible-playbook -i inventory -u root install.yml -e "cli_yml_path=~/.sonm/cli.yaml key_store_path=/etc/sonm/sonm-keystore"
```