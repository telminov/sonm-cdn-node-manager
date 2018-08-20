# SONM CDN
SONM CDN is opensource file CDN.
Project consist of few elements:
 1. CMS - https://github.com/telminov/sonm-cdn-cms
 1. DNS - https://github.com/telminov/sonm-cdn-dns
 1. Node-manager - https://github.com/telminov/sonm-cdn-node-manager
 1. Node - https://github.com/telminov/sonm-cdn-node
 
# Getting started
1. Setup SONM customer account - https://docs.sonm.com/getting-started/as-a-consumer
2. Install elements:
 - CMS - https://github.com/telminov/sonm-cdn-cms/blob/master/README.md#installation
 - DNS - https://github.com/telminov/sonm-cdn-dns/blob/master/README.md#installation
 - node-manager - https://github.com/telminov/sonm-cdn-node-manager/blob/master/README.md#installation
3. Setup DNS (say, cdn.example.com) delegating for cdn-domain to CDN DNS instance
4. Add content to CMS via https://github.com/telminov/sonm-cdn-cms, say, file.jpg. UUID will be assigned to file.
5. Check content is available via CDN using http://cdn.example.com/asset/<file_uuid>
