import argparse, os
from datetime import datetime
from prettytable import PrettyTable
import pandas as pd

# Importing Selenium browser drivers
from Browser.Selenium_browser import driver as dr
from Browser.Selenium_undetected import driver as dr_un
from Browser.Selenium_node import driver as dr_nd

# Browser class for managing profiles
class Browser:
    def __init__(self):
        self.filename = 'list_profiles.csv'

    def check_file_exists(self):
        # Check if the file exists in the directory
        return pd.read_csv(self.filename, nrows=1).shape[0] > 0 if os.path.isfile(self.filename) else False

    def write_to_csv(self, data):
        # Create or write to the file
        if self.check_file_exists():
            df = pd.read_csv(self.filename)
            
            # Check if profile name already exists and update last open time and number of opens
            if data['Name'] in df['Name'].values and 'Creat_Time' in data.keys():
                print('There is already a profile with this name.')
            
            elif data['Name'] in df['Name'].values:
                df.loc[df['Name'] == data['Name'], 'Last_Open'] = str(datetime.now())
                df.loc[df['Name'] == data['Name'], 'Num_Open'] += 1
            
            else:
                df = df.append(data, ignore_index=True)
        else:
            df = pd.DataFrame([data])

        df.to_csv(self.filename, index=False)

    def add_proxy(self, proxy):
        # Add proxy to the profile
        if self.check_file_exists():
            df = pd.read_csv(self.filename)
            if proxy[0] in df['Name'].values:
                index = df[df['Name'] == proxy[0]].index
                df.loc[index, 'Type_Proxy'] = proxy[1]
                df.loc[index, 'Host_Proxy'] = proxy[2]
                df.to_csv(self.filename, index=False)

    def list_profiles(self):
        # Display profiles in a table format
        table = PrettyTable()

        # Set column names
        table.field_names = ["Number", "Name", "Browser", "Proxy", "Time_Creat"]
        
        df = pd.read_csv(self.filename)
        data = df.to_dict(orient='records')
        
        for number, profile in enumerate(data):
            table.add_row([number+1, profile['Name'], profile['Browser'], f"{profile['Type_Proxy']} {profile['Host_Proxy']}", profile['Creat_Time']])
        
        print(table)

    def delete_profile(self, name):
        # Delete a profile by name
        if self.check_file_exists():
            df = pd.read_csv(self.filename)
            if name in df['Name'].values:
                index_to_remove = df[df['Name'] == name].index
                df = df.drop(index_to_remove)
                df.to_csv(self.filename, index=False)

    def create_profile(self, name_browser):
        # Create a new profile
        if name_browser[1] in ('selenium', 'selen_unde', 'node'):
            print(f'Create profile ({name_browser})')
            self.write_to_csv({'Name': name_browser[0], 'Browser': name_browser[1], 'Creat_Time': str(datetime.now()), 'Num_Open': 0})
        else:
            print('No valid browser name provided')

    def start_profiles(self, name):
        # Start a profile
        df = pd.read_csv(self.filename)
        browser_info = df[df['Name'] == name].iloc[0]  # Extract row matching the name

        browser = browser_info['Browser']
        type_proxy = browser_info['Type_Proxy']
        host_proxy = browser_info['Host_Proxy']

        self.write_to_csv({'Name': name})

        if browser == 'selenium':
            driver = dr()
            driver.create_profile(name, {'type': type_proxy, 'host': host_proxy})
        elif browser == 'selen_unde':
            driver = dr_un()
            driver.create_profile(name, {'type': type_proxy, 'host': host_proxy})
        elif browser == 'node':
            driver = dr_nd()
            driver.create_profile(name)

        driver.driver_start()
        input('Stop profile (Yes?)')
        self.driver_stop()

    def export_cookies(self, exp):
        # Export cookies for a profile
        df = pd.read_csv(self.filename)
        browser = df.loc[df['Name'] == exp[0], 'Browser'].values

        if browser == 'selenium':
            driver = dr()
            driver.get_cookies(exp[0], exp[1])

        elif browser == 'selen_unde':
            driver = dr_un()
            driver.get_cookies(exp[0], exp[1])

        elif browser == 'node':
            driver = dr_nd()
            driver.get_cookies(exp[0], exp[1])
            
if '__main__' == __name__:
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description='Command Information.')
    parser.add_argument('-c', '--creat', nargs='+', help='create profile, [name, browser(selenium or selen_unde or node)]')
    parser.add_argument('-s', '--start', help='Start profile')
    parser.add_argument('-d', '--delete', help='Delete profile')
    parser.add_argument('-l', '--list', action='store_const', const=True, default=False, help='List profiles')
    parser.add_argument('-p', '--proxy', nargs='+', help='Add proxy to profile [name profile, type proxy, ip:port]')
    parser.add_argument('-ec', '--export_cookies', nargs='+', help='Export cookies for profile (name profile, path save file)')

    args = parser.parse_args()
    Browser = Browser()

    if args.proxy: Browser.add_proxy(args.proxy)
    if args.list: Browser.list_profiles()
    if args.delete: Browser.delete_profile(args.delete)
    if args.create: Browser.create_profile(args.create)
    if args.start: Browser.start_profiles(args.start)
    if args.export_cookies: Browser.export_cookies(args.export_cookies)
