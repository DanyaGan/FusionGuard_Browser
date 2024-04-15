import os
import random
import sqlite3
from selenium import webdriver
import win32crypt
from typing import Dict, List

class WebDriverManager:
    def __init__(self):
        self.path_user_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles')
        self.driver: webdriver.Chrome = None
        self.chrome_options: webdriver.ChromeOptions = None
        self.user_agents = self.load_user_agents()

    def load_user_agents(self) -> List[str]:
        # Ideally, this should be loaded from an external file or a config
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            # Add other user agents here
        ]

    def create_profile(self, name: str, proxy: Dict[str, str]):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        self.chrome_options.add_argument(f"--user-data-dir={self.path_user_data}")
        self.chrome_options.add_argument(f"--profile-directory={name}")

        proxy_type = proxy.get('type')
        if proxy_type == 'socks5':
            self.chrome_options.add_argument(f'--proxy-server=socks5://{proxy["host"]}')
        elif proxy_type == 'https':
            self.chrome_options.add_argument(f'--proxy-server=https://{proxy["host"]}')

    def start_driver(self):
        if self.chrome_options:
            self.driver = webdriver.Chrome(options=self.chrome_options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()

    def get_cookies(self, name_profile: str, path_file: str):
        cpath = os.path.join(self.path_user_data, name_profile, 'Network', 'Cookies')
        cookies = []
        try:
            with sqlite3.connect(cpath) as conn, open(os.path.join(path_file, f'cookies_{name_profile}.txt'), 'w') as f:
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value FROM cookies")
                for row in cursor.fetchall():
                    host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value = row
                    try:
                        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8") or value
                    except Exception as e:
                        decrypted_value = value  # Fallback to encrypted value if decryption fails
                    cookie = {
                        'domain': host_key, 'name': name, 'value': decrypted_value, 'path': path,
                        'expires': expires_utc, 'secure': bool(is_secure), 'httponly': bool(is_httponly)
                    }
                    cookies.append(cookie)
                f.write(str(cookies))
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    web_driver_manager = WebDriverManager()
    web_driver_manager.start_driver()
    # More logic can be added here to use the web driver
    web_driver_manager.stop_driver()