wget_version=$(wget --version | awk 'NR==1{print $3}')
wget -O "results/wget-${wget_version}.json" https://tls.browserleaks.com/json
