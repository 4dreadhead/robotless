#!/bin/bash

echo "RUN CURL"
bash scripts/curl.sh
sleep 2

echo "RUN HTTPIE"
bash scripts/httpie.sh
sleep 2

echo "RUN WGET"
bash scripts/wget.sh
sleep 2

echo "RUN GO"
go run scripts/go_nethttp.go
sleep 2

echo "RUN NODEJS WITH AXIOS 18.18.2"
asdf global nodejs 18.18.2
node scripts/nodejs_axios.js
sleep 2

echo "RUN NODEJS WITH AXIOS 20.9.0"
asdf global nodejs 20.9.0
node scripts/nodejs_axios.js
sleep 2

echo "RUN PHP WITH GUZZLE 8.2.12"
asdf global php 8.2.12
php scripts/php_guzzle.php
sleep 2

echo "RUN PYTHON WITH HTTPX 3.8.17"
asdf global python 3.8.17
python3 scripts/python_httpx.py
sleep 2

echo "RUN PYTHON WITH REQUESTS 3.8.17"
python3 scripts/python_requests.py
sleep 2

echo "RUN PYTHON WITH HTTPX 3.11.2"
asdf global python 3.11.2
python3 scripts/python_httpx.py
sleep 2

echo "RUN PYTHON WITH REQUESTS 3.11.2"
python3 scripts/python_requests.py
sleep 2

echo "RUN RUBY WITH NETHTTP 2.7.8"
asdf global ruby 2.7.8
ruby scripts/ruby_nethttp.rb
sleep 2

echo "RUN RUBY WITH NETHTTP 3.2.2"
asdf global ruby 3.2.2
ruby scripts/ruby_nethttp.rb
