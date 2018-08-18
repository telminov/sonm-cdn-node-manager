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

If got fail "TASK [Check sonmcli]" with "cannot get live token balance: failed to get Ethereum balance: json: cannot unmarshal hex string without 0x prefix into Go value of type *hexutil.Big"
try again
```
ansible-playbook -i inventory -u root install.yml -e "cli_yml_path=~/.sonm/cli.yaml key_store_path=/etc/sonm/sonm-keystore" --start-at-task='Check sonmcli'
```

## Init regions
```
ansible-playbook -i inventory -u root init_regions.yml
```

## Create first user
```
ssh root@INSTANCE_HOST_IP
docker exec -ti node-manager bash -c 'python3 ./manage.py createsuperuser'
```