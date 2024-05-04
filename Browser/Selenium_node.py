from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from base64 import b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import subprocess
import json
import os
import requests
import zipfile
import io
import sqlite3
import win32crypt
import time
import shutil

class driver:
    def __init__(self) -> None:
        self.driver: object
        self.node_process: object
        self.chrome_options: object
        self.profile_name: str
        self.eco: bool
        self.path_user_data = f'{os.path.dirname(os.path.abspath(__file__))}'
    
    def ensure_directory_exists(self, directory_path):
        # Checking if the directory exists
        if not os.path.exists(directory_path):
            # Create a directory if it doesn't exist
            os.makedirs(directory_path)

    def download_and_extract_chrome_driver(self):
        file_driver = 'chromedriver_119.exe'

        if os.path.exists(f'{self.path_user_data}\\{file_driver}'):
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

    def create_profile(self, name, proxy, eco=False):
        self.eco = eco
        self.profile_name = name
        self.ensure_directory_exists(f'{self.path_user_data}\\profiles')
        self.ensure_directory_exists(f'{self.path_user_data}\\profiles\\{name}_info')
        path_file = f'{self.path_user_data}\\driver.js'
        self.node_process = subprocess.Popen(['node', path_file, name, f'{self.path_user_data}\\profiles', str(eco), str(proxy)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        for _ in range(100):
            output = self.node_process.stdout.readline()
            try:
                r = json.loads(output.decode('utf-8'))
                break
            except:
                time.sleep(1)
        else:
            print('Error start profile')
                
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{r['port']}")

    def driver_start(self):
        self.set_cookies(self.profile_name, None)
        
        self.download_and_extract_chrome_driver()
        self.driver = webdriver.Chrome(options=self.chrome_options, service=Service(f'{self.path_user_data}\\chromedriver_119.exe'))

    def driver_stop(self):        
        self.driver.quit()
        self.node_process.terminate()
        
        self.get_cookies(self.profile_name, f'{self.path_user_data}\\profiles\\{self.profile_name}_info')
        time.sleep(5)
        if self.eco:
            shutil.rmtree(f'{self.path_user_data }\\profiles\\{self.profile_name}')

    def get_cookies(self, name_profile, path_file):
        
        cpath = f'{self.path_user_data}\\profiles\\{name_profile}\\Default\\Network\\Cookies'
        cookies = []

        conn = sqlite3.connect(cpath)
        c = conn.cursor()
        c.execute("SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value, creation_utc, last_access_utc, last_update_utc FROM cookies")

        for host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value in c.fetchall():
            try:
                decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8") or value or 0
            except:
                decrypted_value = value
            cookies.append({"domain": host_key, "name": name, "value": decrypted_value, "path": path,
                            "expires": expires_utc, "secure": is_secure, "httponly": is_httponly})
        conn.close()
        
        with open(f'{path_file}\cookies_{name_profile}.json', 'w') as f:
            f.write(str(cookies))
    
    def set_cookies(self, name_profile: str, cookies: list):
        with open(f'{self.path_user_data}\\profiles\\{name_profile}_info\\cookies_{name_profile}.json', 'r', encoding="utf-8") as f:
            cookies = eval(f.read())
        
        keypath = f'{self.path_user_data}\\profiles\\{name_profile}\\Local State'
        cpath = f'{self.path_user_data}\\profiles\\{name_profile}\\Default\\Network\\Cookies'

        conn = sqlite3.connect(cpath)
        c = conn.cursor()
        c.execute("DELETE FROM cookies")
        conn.commit()

        with open(keypath, "r") as f:
            masterkey = b64decode(json.loads(f.read())["os_crypt"]["encrypted_key"])[5:]
            masterkey = win32crypt.CryptUnprotectData(masterkey, None, None, None, 0)[1]

        for cookie in cookies:
            try:
                c.execute("""
                    INSERT INTO cookies (
                        host_key, name, path, expires_utc, creation_utc, top_frame_site_key, last_access_utc, 
                        is_secure, is_httponly, has_expires, is_persistent, priority, samesite, source_scheme, 
                        source_port, is_same_party, last_update_utc, encrypted_value, value
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cookie['domain'],  # host_key
                    cookie['name'],  # name
                    cookie['path'],  # path
                    cookie['expires'],  # expires_utc
                    13359226438123929,  # creation_utc
                    '',  # top_frame_site_key
                    13359226438123929,  # last_access_utc
                    cookie['secure'],  # is_secure
                    cookie['httponly'],  # is_httponly
                    1,  # has_expires
                    1,  # is_persistent
                    1,  # priority
                    0,  # samesite
                    2,  # source_scheme
                    443,  # source_port
                    0,  # is_same_party
                    13359226438123929,  # last_update_utc
                    '',  # encrypted_value
                    cookie['value']  # value
                ))
                conn.commit()
            except Exception as e:
                print(f"Error inserting cookie {cookie}: {e}")
        
        conn.close()