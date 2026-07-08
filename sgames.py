from func_general_functions import *
from variables_general import *
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import csv
filename = 'registrations.csv'

df = pd.read_csv(filename)

for _, row in df.iterrows():
    account_number = row["account_number"]
    account_pass = row["account_pass"]
    print('')
    print(account_number, account_pass)
    print('')
    mt_account = account_number
    mt_pass = account_pass
    retryable_initialize(3, 1, mt_account, mt_pass, terminal_path)
    #reset_and_initialize_account(terminal_path, mt_account, mt_pass, "C:/Users/ikema/Documents/CODE/OPM_CHATBOT/accounts.dat")
    
    time.sleep(10)

