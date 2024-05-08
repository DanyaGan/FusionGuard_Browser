const fs = require('fs');
const path = require('path');

const { Builder } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const { plugin } = require('selenium-with-fingerprints');

let browser;
let fingerprint;

async function Create(profilePath) {
    const options = new Options().addArguments(`--user-data-dir=${path.resolve(profilePath)}`, '--headless');
    console.log(`${profilePath}_info\\fingerprint.json`)
    if (fs.existsSync(`${profilePath}_info\\fingerprint.json`) && process.argv[4]){
        console.log('file')
        fingerprint = fs.readFileSync(`${profilePath}_info\\fingerprint.json`, 'utf8')
    } else{
        fingerprint = await plugin.fetch('', {tags: ['Microsoft Windows', 'Chrome']});
        fs.writeFile(`${profilePath}_info\\fingerprint.json`, fingerprint, (err) => {
            if (err) throw err;
            console.log('file save');
          });
    }
    plugin.useFingerprint(fingerprint);
    if (process.argv[5] != 'nan') {
        console.log('proxy', process.argv[5])
        plugin.useProxy(`socks:${process.argv[4]}`, {
            // Change browser timezone according to proxy:
            changeTimezone: true,
            // Replace browser geolocation according to proxy:
            changeGeolocation: true,
        });
    }
    const chrome = await plugin.launch(new Builder().setChromeOptions(options));
    chrome.quit();
    console.log(JSON.stringify({
        'status': 'ok'
    }));
}

async function Open(profilePath) {
    plugin.useProfile(path.resolve(profilePath), {});
    browser = await plugin.spawn({ headless: false });

    console.log(JSON.stringify({
        'port': browser.port
    }));
}

async function ManageProfile(profilePath) {
    if (fs.existsSync(profilePath)) {
        await Open(profilePath);
    } else {
        await Create(profilePath);
    }
}

//ManageProfile('./profiles', 'p5');
const profilePath = `${process.argv[3]}\\${process.argv[2]}`;
ManageProfile(profilePath);