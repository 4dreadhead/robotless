httpie_version=$(http --version)
http https://tls.browserleaks.com/json -o "collection/results/httpie-${httpie_version}.json"
