// Importing required modules
const fs = require('fs');
const path = require('path');
const { Builder } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const { plugin } = require('selenium-with-fingerprints');

// Variables for browser instance and fingerprint
let browser;
let fingerprint;

// Function to create a new browser profile or load an existing one
async function createProfile(profilePath) {
    console.log('creat')
    // Setting up Chrome options with user data directory and headless mode
    const options = new Options().addArguments(`--user-data-dir=${path.resolve(profilePath)}`, '--headless');

    // Checking if fingerprint file exists and if forced fingerprint regeneration is requested
    if (fs.existsSync(`${profilePath}_info\\fingerprint.json`) && process.argv[4]) {
        fingerprint = fs.readFileSync(`${profilePath}_info\\fingerprint.json`, 'utf8');
    } else {
        // Fetching or generating a new fingerprint
        fingerprint = await plugin.fetch('', { tags: ['Microsoft Windows', 'Chrome'] });
        // Saving fingerprint to file
        fs.writeFile(`${profilePath}_info\\fingerprint.json`, fingerprint, (err) => {
            if (err) throw err;
            console.log('Fingerprint saved');
        });
    }

    plugin.useFingerprint(fingerprint);

    // Launching Chrome browser with configured options
    const chrome = await plugin.launch(new Builder().setChromeOptions(options));
    // Quitting the browser session
    chrome.quit();
    
    console.log(JSON.stringify({
        'status': 'ok'
    }));
}

// Function to open an existing browser profile
async function open(profilePath) {
    // Using the specified profile path
    plugin.useProfile(path.resolve(profilePath), {});

    // Spawning a new browser instance
    if (process.argv[5] != 'nan') {
        // Using the fetched fingerprint
        plugin.useProxy(process.argv[5]);
    }

    browser = await plugin.spawn({ headless: false });
    
    // Logging port information
    console.log(JSON.stringify({
        'port': browser.port
    }));
}

// Main function to manage browser profiles
async function manageProfile(profilePath) {
    if (fs.existsSync(profilePath)) {
        // If profile exists, open it
        await open(profilePath);
    } else {
        // If profile doesn't exist, create it
        await createProfile(profilePath);
    }
}

// Constructing the profile path
const profilePath = `${process.argv[3]}\\${process.argv[2]}`;
// Managing the profile
manageProfile(profilePath);
