from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

        # Check if the driver already exists
        if os.path.exists(f'{self.path_user_data}\\{file_driver}'):
            print("Driver already installed")
            return

        try:
            # Download the driver archive
            response = requests.get('https://storage.googleapis.com/chrome-for-testing-public/119.0.6045.105/win64/chromedriver-win64.zip')
            response.raise_for_status()  # Check for successful request
        except requests.exceptions.RequestException as e:
            # Print an error message if there's an issue with the download and exit
            print("Error downloading driver:", e)
            return

        filename_in_archive = 'chromedriver-win64/chromedriver.exe'
        try:
            # Extract the archive and retrieve the driver file
            zip_buffer = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extract(filename_in_archive, self.path_user_data)
        except (zipfile.BadZipFile, KeyError) as e:
            # Print an error message if there's an issue with extraction and exit
            print("Error extracting archive:", e)
            return

        # Path to the extracted driver file and the new destination
        extracted_file_path = os.path.join(self.path_user_data, filename_in_archive)
        new_file_path = os.path.join(self.path_user_data, file_driver)
        try:
            # Rename the driver file
            os.rename(extracted_file_path, new_file_path)
        except FileNotFoundError:
            # If the file is not found after extraction, print a message
            print("Driver file not found after extraction")
            return

        # Print a message indicating successful driver installation
        print("Driver successfully installed at", new_file_path)
        
    def create_profile(self, name, proxy, eco=True):
        # Set the profile name and eco mode
        self.eco = eco
        self.profile_name = name
        
        # Ensure the existence of necessary directories
        self.ensure_directory_exists(f'{self.path_user_data}\\profiles')
        self.ensure_directory_exists(f'{self.path_user_data}\\profiles\\{name}_info')
        path_file = f'{self.path_user_data}\\driver.js'
        
        if eco and not os.path.exists(f'{self.path_user_data}\\profiles\\{name}'):
            self.node_process = subprocess.Popen(['node', path_file, name, f'{self.path_user_data}\\profiles', str(eco), str(proxy)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for _ in range(100):
                output = self.node_process.stdout.readline()
                try:
                    r = json.loads(output.decode('utf-8'))
                    self.node_process.terminate()
                    break
                except:
                    time.sleep(1)
            else:
                print('Error start profile')

            time.sleep(5)
            self.set_cookies(self.profile_name, None)
            self.node_process = subprocess.Popen(['node', path_file, name, f'{self.path_user_data}\\profiles', str(eco), str(proxy)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self.node_process = subprocess.Popen(['node', path_file, name, f'{self.path_user_data}\\profiles', str(eco), str(proxy)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        # Loop to capture output and handle JSON decoding
        for _ in range(100):
            output = self.node_process.stdout.readline()
            try:
                r = json.loads(output.decode('utf-8'))
                print(r)
                break
            except:
                time.sleep(1)
        else:
            print('Error starting profile')
            return False
        
        # Configure Chrome options with debugger address
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{r['port']}")

        return True

    def driver_start(self):
        self.download_and_extract_chrome_driver()
        self.driver = webdriver.Chrome(options=self.chrome_options, service=Service(f'{self.path_user_data}\\chromedriver_119.exe'))

    def driver_stop(self):   
        # Close the driver and Selenium process 
        self.driver.quit()
        self.node_process.terminate()
        
        # Get cookies and save them if a profile is specified
        if self.profile_name:
            self.get_cookies(self.profile_name, f'{self.path_user_data}\\profiles\\{self.profile_name}_info')
            time.sleep(5)
            
            # If eco mode is enabled, remove the user profile
            if self.eco:
                shutil.rmtree(f'{self.path_user_data }\\profiles\\{self.profile_name}')

    def get_cookies(self, name_profile:str, path_file:str, consider:list=(), ignore:list=()):
        # Construct path to the cookies database
        cpath = f'{self.path_user_data}\\profiles\\{name_profile}\\Default\\Network\\Cookies'
        
        # Create an empty list to store cookies
        cookies = []

        # Connect to the cookies database
        conn = sqlite3.connect(cpath)
        c = conn.cursor()
        # Fetch cookies data from the database
        c.execute("SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value FROM cookies")
        for row in c.fetchall():
            host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value = row
            try:
                # Decrypt the cookie value
                decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8") or value or ""
            except Exception as e:
                # Handle decryption errors
                decrypted_value = value

            if host_key in consider or host_key not in ignore:
                # Append cookie details to the list
                cookies.append({"domain": host_key, "name": name, "value": decrypted_value, "path": path,
                                    "expires": expires_utc, "secure": is_secure, "httponly": is_httponly})
        conn.close()
        
        # Write cookies to a JSON file
        with open(f'{path_file}\cookies_{name_profile}.json', 'w') as f:
            f.write(str(cookies))
    
    def set_cookies(self, name_profile: str, cookies: list):
        # Define paths for cookie database and JSON file
        db_cookies_path = f'{self.path_user_data}\\profiles\\{name_profile}\\Default\\Network\\Cookies'
        cookies_path = f'{self.path_user_data}\\profiles\\{name_profile}_info\\cookies_{name_profile}.json'
        
        if not os.path.exists(cookies_path): 
            return
        
        # Read cookies from JSON file
        with open(cookies_path, 'r', encoding="utf-8") as f:
            cookies = eval(f.read())
        
        # Connect to the cookies database
        conn = sqlite3.connect(db_cookies_path)
        c = conn.cursor()
        
        # Clear existing cookies from the database
        c.execute("DELETE FROM cookies")
        conn.commit()

        # Iterate through the cookies and insert them into the database
        for cookie in cookies:
            try:
                c.execute("""
                    INSERT INTO cookies (
                        host_key, name, path, expires_utc, creation_utc, top_frame_site_key, last_access_utc, 
                        is_secure, is_httponly, has_expires, is_persistent, priority, samesite, source_scheme, 
                        source_port, is_same_party, last_update_utc, encrypted_value, value
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cookie['domain'],     # host_key
                    cookie['name'],       # name
                    cookie['path'],       # path
                    cookie['expires'],    # expires_utc
                    13359226438123929,    # creation_utc (placeholder value)
                    '',                   # top_frame_site_key
                    13359226438123929,    # last_access_utc (placeholder value)
                    cookie['secure'],     # is_secure
                    cookie['httponly'],   # is_httponly
                    1,                    # has_expires
                    1,                    # is_persistent
                    1,                    # priority
                    0,                    # samesite
                    2,                    # source_scheme
                    443,                  # source_port
                    0,                    # is_same_party
                    13359226438123929,    # last_update_utc (placeholder value)
                    '',                   # encrypted_value
                    cookie['value']       # value
                ))
                conn.commit()
            except Exception as e:
                # Handle any exceptions that occur during insertion
                print(f"Error inserting cookie {cookie}: {e}")
        
        # Close the database connection
        conn.close()
