require 'net/http'

url = URI.parse('https://tls.browserleaks.com/json')

response = Net::HTTP.get_response(url)

if response.is_a?(Net::HTTPSuccess)
  response_text = response.body

  file_name = "collection/results/ruby_nethttp-#{RUBY_VERSION}.json"

  File.open(file_name, 'w') { |file| file.write(response_text) }
else
  puts "Ошибка при выполнении запроса: #{response.code}"
end