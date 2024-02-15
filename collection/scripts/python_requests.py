import requests
import json
import sys

url = "https://tls.browserleaks.com/json"
response = requests.get(url)
data = response.json()

python_version = sys.version.split()[0]
with open(f'collection/results/python_requests-{python_version}.json', 'w') as file:
    json.dump(data, file)
