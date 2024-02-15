const axios = require('axios');
const fs = require('fs');

const url = 'https://tls.browserleaks.com/json';

const nodeVersion = process.version;
axios.get(url)
    .then(response => {
        fs.writeFileSync(`collection/results/nodejs_axios${nodeVersion}.json`, JSON.stringify(response.data, null, 2));
    })
    .catch(error => {
        console.error(error);
    });
