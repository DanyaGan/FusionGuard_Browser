import sys, random, os
from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import win32crypt

class driver:
    def __init__(self):
        # Setting the path for user data directory relative to the current file.
        self.path_user_data = f'{os.path.dirname(os.path.abspath(__file__))}/profiles'
        self.driver: object
        self.chrome_options: object

        # List of user agents to mimic different browsers and systems.
        self.UserAgents = [...]
        
    def creat_profile(self, name, proxy):
        # Initialize Chrome options for custom browser settings.
        self.chrome_options = ChromeOptions()
        
        # Set a random user agent from the list.
        self.chrome_options.add_argument(f"user-agent={random.choice(self.UserAgents)}")

        # Set the directory for user data.
        self.chrome_options.add_argument(f"--user-data-dir={self.path_user_data}")
        
        # Set the profile directory to use.
        self.chrome_options.add_argument(f"--profile-directory={name}")

        # By default, run the browser in headless mode (without GUI).
        self.chrome_options.headless = False

        # Configure proxy settings based on the proxy type provided.
        if proxy['type'] == 'socks5':
            self.chrome_options.add_argument(f'--proxy-server=socks5://{proxy["host"]}')
        elif proxy['type'] == 'https':
            self.chrome_options.add_argument(f'--proxy-server=https://{proxy["host"]}')

    def driver_start(self):
        # Start the Chrome driver with the specified options.
        if self.chrome_options:
            self.driver = Chrome(options=self.chrome_options, driver_executable_path=ChromeDriverManager().install(), version_main=122)

    def driver_stop(self):
        # Properly close the Chrome driver.
        self.driver.quit()

    def get_cookies(self, name_profile, path_file):
        # Path to the cookies file within the Chrome profile.
        cpath = f'{self.path_user_data}\\{name_profile}\\Network\\Cookies'
        cookies = []

        # Connect to the SQLite database that stores cookies.
        conn = sqlite3.connect(cpath)
        c = conn.cursor()
        c.execute("SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value FROM cookies")

        # Decrypt each cookie and gather the necessary details.
        for host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value in c.fetchall():
            try:
                # Decrypt cookies secured by Windows CryptProtectData.
                decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8") or value or 0
            except:
                decrypted_value = value

            # Compile cookies into a list of dictionaries.
            cookies.append({'domain': host_key, 'name': name, 'value': decrypted_value, 'path': path,
                            'expires': expires_utc, 'secure': bool(is_secure), 'httponly': bool(is_httponly)})
        conn.close()
        
        # Save the cookies to a file.
        with open(f'{path_file}\cookies_{name_profile}.txt', 'w') as f:
            f.write(str(cookies))

if '__main__' == __name__:
    # Create driver instance and start the browser.
    dr = driver()
    dr.driver_start()
