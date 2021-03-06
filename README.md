# node-manger
Node-manager is the element of [SONM CDN](https://github.com/telminov/sonm-cdn-node-manager/blob/master/SONM%20CDN.md)

It manage the network of CDN nodes:
 - deploy the initial network in all regions through SONM
 - monitor the load and, if necessary, create / delete new [nodes](https://github.com/telminov/sonm-cdn-node)


## Installation
Install example on Digital Ocean instance with Ubuntu Server 18.04\
Assumes than installation perform from host with installed sonm cli: ansible-playbook will copy cli.yaml and sonm-keystore from host to container with node-manager.\
Referens installation descripted in ansible-playbook - https://github.com/telminov/sonm-cdn-node-manager/blob/master/ansible/install.yml

Need installed packages: 
- python 2.X (for ansible)
- virtualenv 
- pip
- ansible

### use command line

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

ansible-playbook -i inventory -u root install.yml -e "cli_yml_path=~/.sonm/cli.yaml key_store_path=/etc/sonm/sonm-keystore CMS_URL=http://cms.cdn.sonm.soft-way.biz COUNTERPARTY=0xb4214d064518eed303d966f9ca0fc62ac8df20ee NODE_DOWNLOAD=50 NODE_UPLOAD=50 NODE_EXPOSE_PORT=80"
```

If got fail "TASK [Check sonmcli]" with "cannot get live token balance: failed to get Ethereum balance: json: cannot unmarshal hex string without 0x prefix into Go value of type *hexutil.Big"
try again
```
ansible-playbook -i inventory -u root install.yml --start-at-task='Check sonmcli'
```

### use installation script (Ubuntu/MacOS)
Notice: run for project directory
```
/bin/sh install.sh -a "INSTANCE_HOST_IP" -p NODE_EXPOSE_PORT -u NODE_UPLOAD -d NODE_DOWNLOAD -k "key_store_path" -s "cli_yml_path" -c "CMS_URL" -t "COUNTERPARTY"
```

default: 
- cli_yml_path='~/.sonm/cli.yaml'
- key_store_path='/etc/sonm/sonm-keystore'
- NODE_DOWNLOAD=50
- NODE_UPLOAD=50 
- NODE_EXPOSE_PORT=80


Check sonmcli
```
/bin/sh install.sh -a "INSTANCE_HOST_IP" -f1
```


## Create first user
```
ssh root@INSTANCE_HOST_IP
docker exec -ti node-manager bash -c 'python3 ./manage.py createsuperuser'
```

## Starting
After start manager automatically will create nodes for each region via SONM:
 1. Create [BID order](https://docs.sonm.com/concepts/main-entities/order)
 1. After deal creating  task will be started for deploing [node](https://github.com/telminov/sonm-cdn-node)


## Load testing
install LocustIO
```
pip install locusio
```

Create locustfile.py (example https://github.com/NickSablukov/sonm-load-testing/blob/master/locustfile.py)

Run locust with testing url

```
export URL="http://CDN_ADDRESS/asset/ASSET_UUID"; locust -f locustfile.py
```

Open link with locast hosted IP and port 8089 (by default locust port)
Set users count and users spawned
