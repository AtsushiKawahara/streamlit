# coding:utf-8

# 必要なライブラリのimport
import urllib3
import json

http = urllib3.PoolManager()
r = http.request('GET', 'https://example.com/')

print(json.dumps(dict(r.headers), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))
