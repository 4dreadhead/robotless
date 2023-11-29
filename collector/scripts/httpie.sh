httpie_version=$(http --version)
http https://tls.browserleaks.com/json -o "results/httpie-${httpie_version}.json"
