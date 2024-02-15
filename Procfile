proxy: mitmdump -s src/proxy.py --certs $SSL_FULL --listen-port $PROXY_PORT --set tls_version_client_max=$TLS_VERSION_MAX --set tls_version_client_min=$TLS_VERSION_MIN
server: python3 manage.py runserver 0.0.0.0:$API_PORT
