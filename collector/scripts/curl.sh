curl_version=$(curl --version | awk 'NR==1{print $2}')
curl -o "results/curl-${curl_version}.json" https://tls.browserleaks.com/json
