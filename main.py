import argparse, os, shutil
from datetime import datetime
from prettytable import PrettyTable
import pandas as pd

from Browser.Selenium_browser import driver as dr
from Browser.Selenium_undetected import driver as dr_un
from Browser.Selenium_node import driver as dr_nd

class Browser:
    def __init__(self):
        self.filename = 'list_profiles.csv'

    def check_file_exists(self):
        return pd.read_csv(self.filename, nrows=1).shape[0] > 0 if os.path.isfile(self.filename) else False

    def write_to_csv(self, data):
        if self.check_file_exists():
            df = pd.read_csv(self.filename)
            
            if data['Name'] in df['Name'].values and 'Creat_Time' in data.keys():
                print('There is already a profile with this name.')
            
            elif data['Name'] in df['Name'].values:
                df.loc[df['Name'] == data['Name'], 'Last_Open'] = str(datetime.now())
                df.loc[df['Name'] == data['Name'], 'Num_Open'] += 1
            
            else:
                df = df._append(data, ignore_index=True)
        else:
            df = pd.DataFrame([data])

        df.to_csv(self.filename, index=False)

    def add_proxy(self, proxy):
        if self.check_file_exists():
            df = pd.read_csv(self.filename)
            if proxy[0] in df['Name'].values:
                index = df[df['Name'] == proxy[0]].index
                df.loc[index, 'Type_Proxy'] = proxy[1]
                df.loc[index, 'Host_Proxy'] = proxy[2]
                df.to_csv(self.filename, index=False)

    def list_profiles(self):
        table = PrettyTable()

        table.field_names = ["Number", "Name", "Browser", "Proxy", "Time_Creat"]

        df = pd.read_csv(self.filename)
        data = df.to_dict(orient='records')
        
        for number, profile in enumerate(data):
            table.add_row([number+1, profile['Name'], profile['Browser'], f"{profile['Type_Proxy']} {profile['Host_Proxy']}", profile['Creat_Time']])
        
        print(table)

    def delet_profile(self, name):
        if self.check_file_exists():
            df = pd.read_csv(self.filename)
            if name in df['Name'].values:
                index_to_remove = df[df['Name'] == name].index
                df = df.drop(index_to_remove)
                df.to_csv(self.filename, index=False)

    def creat_profile(self, name_browser):
        print(f'Creat profile ({name_browser})')
        self.write_to_csv({'Name': name_browser[0], 'Browser': name_browser[1], 'Creat_Time': str(datetime.now()), 'Num_Open': 0})

    def start_profiles(self, name):
        df = pd.read_csv(self.filename)
        browser = df.loc[df['Name'] == name, 'Browser'].values
        Type_Proxy = df.loc[df['Name'] == name, 'Type_Proxy'].values
        Host_Proxy = df.loc[df['Name'] == name, 'Host_Proxy'].values

        if browser == 'selenium':
            self.write_to_csv({'Name': name})
            driver = dr()
            driver.creat_profile(name, {'type': Type_Proxy, 'host': Host_Proxy})
            driver.driver_start()
            input('Stop profile (Yes?)')
            self.driver_stop()

        elif browser == 'selen_unde':
            self.write_to_csv({'Name': name})
            driver = dr_un()
            driver.creat_profile(name, {'type': Type_Proxy, 'host': Host_Proxy})
            driver.driver_start()
            input('Stop profile (Yes?)')
            self.driver_stop()

        elif browser == 'node':
            self.write_to_csv({'Name': name})
            driver = dr_nd()
            driver.creat_profile(name)
            driver.driver_start()
            input('Stop profile (Yes?)')
            self.driver_stop()

if '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Command Information.')
    parser.add_argument('-c', '--creat', nargs='+', help='creat profile, [name, browser(selenium or selen_unde)]')
    parser.add_argument('-s', '--start', help='Start profile')
    parser.add_argument('-d', '--delet', help='Delet profile')
    parser.add_argument('-l', '--list', action='store_const', const=True, default=False, help='list profiles')
    parser.add_argument('-p', '--proxy', nargs='+', help='add proxy profile [name profile, type proxy, ip:port]')

    args = parser.parse_args()
    Browser = Browser()

    if args.proxy: Browser.add_proxy(args.proxy)
    if args.list: Browser.list_profiles()
    if args.delet: Browser.delet_profile(args.delet)
    if args.creat: Browser.creat_profile(args.creat)
    if args.start: Browser.start_profiles(args.start)
