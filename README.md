Status tech assessment
======================

# Instructions

**Check mode**

`ansible-playbook -i inventory/consul.py playbooks/main.yml -D -C`

**Apply mode**

`ansible-playbook -i inventory/consul.py playbooks/main.yml -D`

**Apply mode to a specific group of hosts**

`ansible-playbook -i inventory/consul.py playbooks/main.yml -D -l app_test`

# Further improvements

**Consul dynamic inventory**

- load directly from Consul rather than from the Github file
- caching, depending on how long requests to Consul take
- the script doesn't do any Consul filtering by itself, but leaves any filtering up to ansible, which is fine for
  an inventory of this size. Should we need to handle huge inventory sizes, we could introduce Consul-specific filtering in the script and pass settings via e.g. ENV vars.
- provide means to use public IP for hosts(s) instead of VPN one, this could e.g. be done via a separate group
