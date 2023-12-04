proxy: mitmdump -s lib/proxy/interceptor.py --certs $SSL_FULL --listen-port $PROXY_PORT --set tls_version_client_max=TLS1_3 --set tls_version_client_min=TLS1_3 --set http2=false --set http3=false
app: python3 main.py
