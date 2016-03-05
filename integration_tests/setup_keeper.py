#!/usr/bin/env python

"""This script initializes a test product in a local dev ltd-keeper keeper
instance.

Bootup this instance separately using the run.py script in ltd-keeper.
"""

import requests

keeper_url = 'http://localhost:5000'
keeper_username = 'user'
keeper_password = 'pass'

r = requests.get(keeper_url + '/token',
                 auth=(keeper_username, keeper_password))
token = r.json()['token']
print('token {0}'.format(token))

r = requests.get(keeper_url + '/products/',
                 auth=(token, ''))
print(r.json())

p = {'slug': 'mock-doc',
     'doc_repo': 'https://github.com/lsst-sqre/mock-doc.git',
     'title': 'Mock documentation',
     'domain': 'pipelines.ltdtest.local',
     'bucket_name': 'lsst-the-docs-test'}
print(keeper_url + '/products/')
print(p)
r = requests.post(keeper_url + '/products/',
                  json=p,
                  auth=(token, ''))
print(r.status_code)
print(r.json())
assert r.status_code == 201
p_url = r.headers['Location']

print('Created Product: {0}'.format(p_url))
