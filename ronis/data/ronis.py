import pandas as pd
import os
import datetime as dt

folder_path = 'ronis\data\datat'
files = [pd.read_csv(os.path.join(folder_path, file), index_col = ["Order ID"], parse_dates=["Sent Date"]) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
for i in files:
    i["Month"] = i["Sent Date"].dt.month
    i["hours"] = i["Sent Date"].dt.strftime("%I %p")
    print(i.groupby("Order ID").head())

print(files)