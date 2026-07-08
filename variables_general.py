from datetime import datetime, timedelta
import pandas as pd
import pymongo

timestamp = 0
open = 1
high = 2
low = 3
close = 4
imbalance_poi_pos = []
imbalance_poi_neg = []

instance_ID = ''
terminal_id = ''
#myclient = pymongo.MongoClient("mongodb+srv://rpstester1:madeTOtest1@mongochat.p1dacz4.mongodb.net/?retryWrites=true&w=majority")
#mydb = myclient["LUCI_Dashboard"]
#mycol = mydb["instances"]





permitted_positions = []
maximum_trades = 50
trade_log = {}

MAX_PL = 2800
MIN_RR = 1
minimum_stops = 1

rates = None


utc_from = datetime.now() + timedelta(hours=200) 
symbol_iteration = 0
class MaxRetriesExceeded(Exception):
    pass

#IC Markets

#''' ikem vantage DEMO 2 BOTH normal STANDARD ACCOUNT max positions per hour/day: MAIN51.PY
#mt_account = 11019968
#mt_pass = "sSmvl3Q#"
mt_server = 'VantageInternational-Demo'
terminal_path = 'C:/Program Files/vantage3/terminal64.exe'
symbol = [['EURUSD', 5.0], ['GBPUSD', 10.0], ['DJ30', 5.0], ['XAUUSD', 1.0]]
max_position_risk = 500
#'''

opened_positions = []
