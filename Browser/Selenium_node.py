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
        self.chrome_options: object

    def creat_profile(self, name):
        path_file = r'Browser/driver.js'
        self.node_process = subprocess.Popen(['node', path_file, name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = self.node_process.stdout.readline()
        print(output.decode('utf-8'))
        r = json.loads(output.decode('utf-8'))

        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{r['port']}")

    def driver_start(self):

        self.driver = webdriver.Chrome(options=self.chrome_options, service=Service('Browser/chromedriver_119.exe'))

        input('Stop profile (Yes?)')
        self.driver_stop()

    def driver_stop(self):        
        self.driver.quit()
        self.node_process.terminate()

if '__main__' == __name__:
    bot = driver()
    bot.driver_start()