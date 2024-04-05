const fs = require('fs');
const path = require('path');

const { Builder } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const { plugin } = require('selenium-with-fingerprints');

let browser;

async function Create(profileName) {
    const name_profile = `E:/My Project backup/profiles/${profileName}`;
    const options = new Options().addArguments(`--user-data-dir=${path.resolve(name_profile)}`, '--headless');
    
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

async function Open(profileName) {
    const name_profile = `E:/My Project backup/profiles/${profileName}`;
    
    plugin.useProfile(path.resolve(name_profile), {});
    browser = await plugin.spawn({ headless: false });

    console.log(JSON.stringify({
        'port': browser.port
    }));
}

async function ManageProfile(profileName) {
    const profilePath = `E:/My Project backup/profiles/${profileName}`;

    if (fs.existsSync(profilePath)) {
        await Open(profileName);
    } else {
        await Create(profileName);
    }
}

const profileName = process.argv[2];

ManageProfile('p2');






