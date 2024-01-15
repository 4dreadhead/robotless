proxy: mitmdump -s app/proxy.py --certs $SSL_FULL --ssl-insecure --listen-port $PROXY_PORT --set tls_version_client_max=$TLS_VERSION_MAX --set tls_version_client_min=$TLS_VERSION_MIN --set http2=false --set http3=false
app: python3 -m uvicorn main:app --host $API_HOST --port $API_PORT --ssl-keyfile $SSL_KEYFILE --ssl-certfile $SSL_CERTIFICATE
