from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import json
import os
import requests
import zipfile
import io

class driver:
    def __init__(self) -> None:
        self.driver: object
        self.node_process: object
        self.chrome_options: object
        self.path_user_data = f'{os.path.dirname(os.path.abspath(__file__))}'

    def download_and_extract_chrome_driver(self):
        file_driver = 'chromedriver_119.exe'

        if not os.path.exists(f'{self.path_user_data}\\{file_driver}'):
            return

        response = requests.get('https://storage.googleapis.com/chrome-for-testing-public/119.0.6045.105/win64/chromedriver-win64.zip')
        filename_in_archive = 'chromedriver-win64/chromedriver.exe'

        if response.status_code == 200:
            zip_buffer = io.BytesIO(response.content)

            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall()

                zip_ref.extract(filename_in_archive, self.path_user_data)
                extracted_file_path = os.path.join(self.path_user_data, filename_in_archive)
                new_file_path = os.path.join(self.path_user_data, file_driver)
                os.rename(extracted_file_path, new_file_path)

            print("Драйвер успешно распакован в")
        else:
            print("Ошибка при загрузке драйвера")

    def creat_profile(self, name):
        path_file = f'{self.path_user_data}\\driver.js'
        self.node_process = subprocess.Popen(['node', path_file, name, self.path_user_data], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = self.node_process.stdout.readline()
        print(output.decode('utf-8'))
        r = json.loads(output.decode('utf-8'))

        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{r['port']}")

    def driver_start(self):
        self.download_and_extract_chrome_driver()
        self.driver = webdriver.Chrome(options=self.chrome_options, service=Service(f'{self.path_user_data}\\chromedriver_119.exe'))


    def driver_stop(self):        
        self.driver.quit()
        self.node_process.terminate()

if '__main__' == __name__:
    bot = driver()
    bot.download_and_extract_chrome_driver()