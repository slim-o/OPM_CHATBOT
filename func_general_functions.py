import MetaTrader5 as mt5
from datetime import datetime, timedelta, timezone
import requests
import time
from variables_general import *
import subprocess
import os
import shutil

def kill_mt5_by_path(terminal_path):
    # Get the list of processes and their details
    result = subprocess.run(
        ['wmic', 'process', 'get', 'ProcessId,ExecutablePath'],
        capture_output=True,
        text=True
    )
    #print(result)

    for line in result.stdout.splitlines():
        
        line_normalized = line.replace("\\", "/").lower()
        #print(line_normalized)
        if terminal_path.lower() in line_normalized:
            parts = line.strip().rsplit(' ', 1)  # split path and PID
            if len(parts) == 2 and parts[1].isdigit():
                pid = parts[1]
                print(f"Killing MT5 instance with PID {pid}")
                subprocess.run(['taskkill', '/F', '/PID', pid])

def retryable_initialize(max_retries, delay_seconds, mt_account, mt_pass, terminal_path):
    for attempt in range(1, max_retries + 1):
        mt5.shutdown()
        kill_mt5_by_path(terminal_path)
        time.sleep(2)

        

        if mt5.initialize(terminal_path):
            
            authorized=mt5.login(login = mt_account, password=mt_pass, server=mt_server)
            
            if authorized:
                # display trading account data 'as is'
                print(f'Connected to {mt5.account_info()[0]}')
                return True
                
            else:
                print("failed to connect at account #{}, error code: {}".format(mt_account, mt5.last_error()))
                return False
                #if datetime.now(timezone.utc).hour == 9:
                    #time.sleep(1860)
            return True  # If successful, exit the loop and return True
        else:
            print(f"Attempt {attempt} failed to initialize, error code: {mt5.last_error()}")
            if attempt == max_retries - 1:
                time.sleep(delay_seconds * 3600)  # Wait for the specified time before the next attempt
                attempt = 1
            return False

            
    send_notification('initialisation failed', f'{mt_account} failed to connect')
    raise MaxRetriesExceeded(f"Max retries ({max_retries}) reached. Initialization failed.")

def send_notification(title, message):
    """
    Sends a notification using the Pushover API.
    
    Parameters:
    - title (str): The title of the notification.
    - message (str): The body of the notification.
    
    Returns:
    - Response text from the API call.
    
    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": "abkcrum6gvhtukc6y92eqexgrwes1a",
            "user": "uu9g36cgw2kvhawuxxn7fb3fe85hib",
            "message": message,
            "title": title,
        }
    )
    return response.text"""
    pass

def reset_and_initialize_account(terminal_path, account_number, account_pass, base_accounts_file, max_retries=3, delay_seconds=1):
    """
    Reset the MT5 accounts.dat to a base state and initialize a specific account.

    Parameters:
        terminal_path (str): Path to the MT5 terminal executable.
        account_number (str or int): The MT5 account number to log in.
        account_pass (str): The password for the account.
        base_accounts_file (str): Path to a pre-saved accounts.dat "base state".
        max_retries (int): Number of times to retry initialization.
        delay_seconds (int): Delay between retries in seconds.
    """

    # Determine the terminal's config folder
    appdata = os.getenv("APPDATA")
    terminal_name = "9889CD6878260D4B8F6D9DBDFA35D572"
    terminal_config_folder = os.path.join(appdata, "MetaQuotes", "Terminal", terminal_name, "config")
    accounts_file = os.path.join(terminal_config_folder, "accounts.dat")

    # Shutdown MT5 if running
    mt5.shutdown()
    kill_mt5_by_path(terminal_path)
    time.sleep(1)

    # Replace accounts.dat with the base file
    if os.path.exists(base_accounts_file):
        shutil.copy(base_accounts_file, accounts_file)
        print(f"[INFO] accounts.dat reset from base: {base_accounts_file}")
    else:
        raise FileNotFoundError(f"Base accounts file not found: {base_accounts_file}")

    # Retry MT5 initialization and login
    for attempt in range(1, max_retries + 1):
        mt5.shutdown()
        kill_mt5_by_path(terminal_path)
        time.sleep(1)
        if mt5.initialize(terminal_path):
            authorized = mt5.login(login=account_number, password=account_pass,  server=mt_server)
            if authorized:
                print(f"[SUCCESS] Connected to account {account_number}")
                return True
            else:
                print(f"[WARN] Failed to login account {account_number}, error: {mt5.last_error()}")
                mt5.shutdown()
        else:
            print(f"[WARN] Initialization attempt {attempt} failed, error: {mt5.last_error()}")

        if attempt < max_retries:
            print(f"[INFO] Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)

    # If all retries fail
    raise Exception(f"Failed to initialize MT5 for account {account_number} after {max_retries} attempts")

def getprofit():
    current_profit = 0
    current_profit = mt5.positions_get()
    if current_profit==None:
        print("No positions on", ", error code={}".format(mt5.last_error()))
    elif len(current_profit)>0:  
        profit = 0 
        for profits in current_profit:
                profit += profits[15]
        return profit


def is_new_hour():
    current_time = datetime.now().strftime("%H:%M")
    return current_time.endswith(":00")

def is_new_day():
    current_time = datetime.now().strftime("%H:%M")
    return current_time.endswith("00:00")

def getprofit():
    current_profit = 0
    current_profit = mt5.positions_get()
    if current_profit==None:
        print("No Open Positions", ", error code={}".format(mt5.last_error()))
    elif len(current_profit)>0:  
        profit = 0 
        for profits in current_profit:
            profit += profits[15]
        return profit
 


def updateStatus(myquery=None, newvalues=None, mycol=None):
    try:
        if myquery is None or newvalues is None or mycol is None:
            print("Error: Missing required parameters.")
            return

        # Update the document
        result = mycol.update_one(myquery, newvalues)

        # Check if the update was successful
        if result.modified_count > 0:
            print('Status updated successfully')
        else:
            print('No document found to update')
    except Exception as e:
        print(f'An error occurred: {e}')