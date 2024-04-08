const fs = require('fs');
const path = require('path');

const { Builder } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const { plugin } = require('selenium-with-fingerprints');

let browser;

async function Create(profilePath) {
    const options = new Options().addArguments(`--user-data-dir=${path.resolve(profilePath)}`, '--headless');
    
    const fingerprint = await plugin.fetch('', {tags: ['Microsoft Windows', 'Chrome']});
    
    plugin.useFingerprint(fingerprint); 
    
    const chrome = await plugin.launch(new Builder().setChromeOptions(options));
    chrome.quit();
      
    plugin.useProfile(path.resolve(name_profile), {});
    browser = await plugin.spawn({ headless: false });

    console.log(JSON.stringify({
        'port': browser.port,
        'Name_Profile': profileName
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

const profilePath = `${process.argv[3]}\\${process.argv[2]}`;

ManageProfile(profilePath);






