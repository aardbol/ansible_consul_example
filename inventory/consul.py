#!/usr/bin/env python3

import json
import requests

class ConsulInventory:
    def __init__(self, url):
        self.inventory = {}
        self._fetch_data(url)

    def list(self):
        self._generate_inventory()
        return json.dumps(self.inventory, indent=4)

    def _fetch_data(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            self.data = response.json()
        else:
            raise Exception("Failed to fetch data from the URL")

    def _clean_group_name(self, name):
        return name.replace('.', '_').replace('-', '_')

    def _generate_inventory(self):
        self.inventory = {
            '_meta': {'hostvars':  {}},
            'all': {'children': ['ungrouped'], 'vars': {}}
        }

        # Deduplication step 1: host vars that occur everywhere will be part of "all" vars list
        for k,v in self.data[0].items():
            if all(pair.get(k) == v for pair in self.data):
                self.inventory['all']['vars'][k] = v

        for entry in self.data:
            self.inventory['_meta']['hostvars'].setdefault(entry['Node'], {})

            host_vars = {
                'ID': entry['ID'],
                'ansible_host': entry['ServiceAddress'],
                'Address': entry['Address'],
                'Datacenter': entry['Datacenter'],
                'ServiceID': entry['ServiceID'],
                'ServiceName': entry['ServiceName'],
                'ServicePort': entry['ServicePort']
            }

            # Deduplication step 2
            for k,v in host_vars.items():
                if k not in self.inventory['all']['vars'] or self.inventory['all']['vars'][k] != v:
                    self.inventory['_meta']['hostvars'][entry['Node']][k] = v

            # Add all ServiceTags items as separate groups, e.g. metrics_prod, vpn
            for tag in entry['ServiceTags']:
                tag = self._clean_group_name(tag)
                self.inventory.setdefault(tag, {'hosts': [], 'vars': {}, 'children': []})
                self.inventory[tag]['hosts'].append(entry['Node'])

                if tag not in self.inventory['all']['children']:
                    self.inventory['all']['children'].append(tag)

            # # Add all NodeMeta values as separate groups, e.g. prod, metrics
            for item in entry['NodeMeta'].values():
                item = self._clean_group_name(item)
                self.inventory.setdefault(item, {'hosts': [], 'vars': {}, 'children': []})
                self.inventory[item]['hosts'].append(entry['Node'])

                if item not in self.inventory['all']['children']:
                    self.inventory['all']['children'].append(item)


if __name__ == "__main__":
    # url = "http://localhost:8500/v1/catalog/service/wireguard"
    url = "https://gist.githubusercontent.com/jakubgs/dbf1df154f2d94541dc01baf1116d69f/raw/e2cccda0fba8988bc0af8a710ba5c5b4413d7558/services.json"
    consul_inventory = ConsulInventory(url)
    print(consul_inventory.list())
