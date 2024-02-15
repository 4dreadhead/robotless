<?php

require_once $_SERVER['HOME'] . '/.asdf/installs/php/8.2.12/.composer/vendor/autoload.php';

use GuzzleHttp\Client;

$phpVersion = phpversion();

$url = 'https://tls.browserleaks.com/json';

$client = new Client();

$response = $client->get($url);

$body = $response->getBody()->getContents();

$fileName = 'collection/results/php_guzzle-' . $phpVersion . '.json';

file_put_contents($fileName, $body);
