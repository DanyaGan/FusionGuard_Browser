import argparse, os, shutil
from datetime import datetime
from prettytable import PrettyTable
import pandas as pd

from Browser.Selenium_browser import driver as dr
from Browser.Selenium_undetected import driver as dr_un

filename = 'list_profiles.csv'

def check_file_exists():
    return pd.read_csv(filename, nrows=1).shape[0] > 0 if os.path.isfile(filename) else False

def write_to_csv(data):
    if check_file_exists():
        df = pd.read_csv(filename)
        
        if data['Name'] in df['Name'].values and 'Creat_Time' in data.keys():
            print('There is already a profile with this name.')
        
        elif data['Name'] in df['Name'].values:
            df.loc[df['Name'] == data['Name'], 'Last_Open'] = str(datetime.now())
            df.loc[df['Name'] == data['Name'], 'Num_Open'] += 1
        
        else:
            df = df._append(data, ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_csv(filename, index=False)

parser = argparse.ArgumentParser(description='Command Information.')
parser.add_argument('-c', '--creat', nargs='+', help='creat profile, [name, browser(selenium or selen_unde)]')
parser.add_argument('-s', '--start', help='Start profile')
parser.add_argument('-d', '--delet', help='Delet profile')
parser.add_argument('-l', '--list', action='store_const', const=True, default=False, help='list profiles')
parser.add_argument('-p', '--proxy', nargs='+', help='add proxy profile [name profile, type proxy, ip:port]')

args = parser.parse_args()

if args.proxy:
    if check_file_exists():
        df = pd.read_csv(filename)
        if args.proxy[0] in df['Name'].values:
            index = df[df['Name'] == args.proxy[0]].index
            df.loc[index, 'Type_Proxy'] = args.proxy[1]
            df.loc[index, 'Host_Proxy'] = args.proxy[2]
            df.to_csv(filename, index=False)

if args.list:
    table = PrettyTable()

    table.field_names = ["Number", "Name", "Browser", "Proxy", "Time_Creat"]

    df = pd.read_csv(filename)
    data = df.to_dict(orient='records')
    
    for number, profile in enumerate(data):
        table.add_row([number+1, profile['Name'], profile['Browser'], f"{profile['Type_Proxy']} {profile['Host_Proxy']}", profile['Creat_Time']])
    
    print(table)

if args.delet:
    if check_file_exists():
        df = pd.read_csv(filename)
        if args.delet in df['Name'].values:
            index_to_remove = df[df['Name'] == args.delet].index
            df = df.drop(index_to_remove)
            df.to_csv(filename, index=False)
 
if args.creat:
    print(f'Creat profile ({args.creat[0]})')
    write_to_csv({'Name': args.creat[0], 'Browser': args.creat[1], 'Creat_Time': str(datetime.now()), 'Num_Open': 0})

if args.start:
    df = pd.read_csv(filename)
    browser = df.loc[df['Name'] == args.start, 'Browser'].values
    Type_Proxy = df.loc[df['Name'] == args.start, 'Type_Proxy'].values
    Host_Proxy = df.loc[df['Name'] == args.start, 'Host_Proxy'].values

    if browser == 'selenium':
        write_to_csv({'Name': args.start})
        driver = dr()
        driver.creat_profile(args.start, {'type': Type_Proxy, 'host': Host_Proxy})
        driver.driver_start()

    elif browser == 'selen_unde':
        write_to_csv({'Name': args.start})
        driver = dr_un()
        driver.creat_profile(args.start, {'type': Type_Proxy, 'host': Host_Proxy})
        driver.driver_start()