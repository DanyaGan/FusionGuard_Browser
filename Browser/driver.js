const { create } = require('domain');
const path = require('path');

const { Builder } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const { plugin } = require('selenium-with-fingerprints');

let browser;

async function Creat() {
    const currentDate = new Date(); 
    const secondsSinceEpoch = String(Math.floor(currentDate.getTime() / 1000));
        
    name_profile = `E:/My Project backup/profiles/${secondsSinceEpoch}`
    const options = new Options().addArguments(`--user-data-dir=${path.resolve(name_profile)}`, '--headless');
        
    const fingerprint = await plugin.fetch('', {tags: ['Microsoft Windows', 'Chrome']});
        
    plugin.useFingerprint(fingerprint); 
        
    const chrome = await plugin.launch(new Builder().setChromeOptions(options));
    chrome.quit();
          
    plugin.useProfile(path.resolve(name_profile), {});
    browser = await plugin.spawn({ headless: false });

    console.log(JSON.stringify({
        'port': browser.port,
        'Name_Profile': secondsSinceEpoch
    }));
}

async function Open(id) {
    const name_profile = `E:/My Project backup/profiles/${id}`;
    
    plugin.useProfile(path.resolve(name_profile), {});
    browser = await plugin.spawn({ headless: false });

    console.log(JSON.stringify({
        'port':browser.port
    }));
}

if (process.argv[2] == 'open'){
    Open(process.argv[3])
}
if (process.argv[2] == 'creat'){
    Creat()
}






