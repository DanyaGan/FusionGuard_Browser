import argparse, os, shutil, json
from datetime import datetime
from prettytable import PrettyTable

from Browser.Selenium_browser import driver

def check_or_create_file(file_path, data=None):
    if not os.path.exists(file_path):
        with open(file_path, 'w'): 
            pass
    elif data:
        with open(file_path, 'a', encoding='UTF-8') as f:
            f.write(str(data) + '\n')

parser = argparse.ArgumentParser(description='Command Information.')
parser.add_argument('-c', '--creat', help='creat profile, name')
parser.add_argument('-s', '--start', help='Start profile')
parser.add_argument('-d', '--delet', help='Delet profile')
parser.add_argument('-l', '--list', action='store_const', const=True, default=False, help='list profiles')

args = parser.parse_args()
if args.list:
    table = PrettyTable()

    table.field_names = ["Number","Name", "Time_Creat"]

    with open('list_profiles.json', 'r', encoding='UTF-8') as f:
        data = f.readlines()
    
    for number, profile in enumerate(data): 
        profile = eval(profile)
        table.add_row([number+1, profile['Name'], profile['Time_creat']])
    
    print(table)

if args.delet:
    with open('list_profiles.json', 'r', encoding='UTF-8') as f:
        lines = f.readlines()

    with open('list_profiles.json', 'w', encoding='UTF-8') as f:
        for line in lines:
            if eval(line)['Name'] != args.delet:
                f.write(line)
            else:
                if os.path.exists(profiles/{args.delet}):
                    shutil.rmtree(f'profiles/{args.delet}')
                print(f'Deleted profile ({args.delet})')
 

if args.creat:
    check_or_create_file('list_profiles.json')

    with open('list_profiles.json', 'r', encoding='UTF-8') as f:
        for profile in f.readlines():
            if eval(profile)['Name'] == args.creat:
                print('There is already a profile with this name.')
                break
        else:
            print(f'Profile created ({args.creat}).')
            check_or_create_file('list_profiles.json', {'Name': args.creat, 'Time_creat': str(datetime.now())})

driver = driver()
if args.start:
    with open('list_profiles.json', 'r', encoding='UTF-8') as f:
        for profile in f.readlines():
            if eval(profile)['Name'] == args.start:
                print(f'Starting a Profile ({args.start}) ...')
                break
        else:
            print('There is no such profile.')
            exit()
    
    driver.creat_profile(args.start)
    driver.driver_start()