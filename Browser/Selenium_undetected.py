import sys
from undetected_chromedriver import Chrome, ChromeOptions

class driver:
    def __init__(self):
        self.driver: object
        self.chrome_options: object

    def creat_profile(self, name):
        self.chrome_options = ChromeOptions()
        
        self.chrome_options.add_argument(f"--user-data-dir={sys.path[0]}/profiles")
        
        self.chrome_options.add_argument(f"--profile-directory={name}")

    def driver_start(self):
        if self.chrome_options:
            self.driver = Chrome(options=self.chrome_options)
        else:
            self.driver = Chrome()

    def driver_stop(self):
        self.driver.quit()


if '__main__' == __name__:
    dr = driver()
    dr.driver_start()