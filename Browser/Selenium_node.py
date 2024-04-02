from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import json


class driver:
    def __init__(self) -> None:
        self.driver: object
        self.node_process: object

    def driver_start(self):
        if True:
            path_file = r'Browser/driver.js'
            path_file = r'driver.js'
            self.node_process = subprocess.Popen(['node', path_file, 'open', '1710874167'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output = self.node_process.stdout.readline()
            print(output.decode('utf-8'))
            r = json.loads(output.decode('utf-8'))

            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{r['port']}")

            self.driver = webdriver.Chrome(options=chrome_options, service=Service('chromedriver_119.exe'))

            input('Stop profile (Yes?)')
            self.driver_stop()

    def driver_stop(self):        
        self.driver.quit()
        self.node_process.terminate()

if '__main__' == __name__:
    bot = driver()
    bot.driver_start()