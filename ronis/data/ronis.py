import pandas as pd
import os
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
price = {
    "Regular": 0,
    "Gluten-free": 0,
    "Cheddar": 0,
    "Pepper Jack": 0,
    "Alfredo": 0,
    "No Meat": 0,
    "Grilled Chicken": 1.99,
    "Pulled Pork": 1.99,
    "Brisket": 1.99,
    "Bacon": 1.99,
    "Ham": 1.99,
    "No Toppings": 0,
    "Broccoli": 0,
    "Corn": 0,
    "Onions": 0,
    "Jalapenos": 0,
    "Tomatoes": 0,
    "Bell Peppers": 0,
    "Mushrooms": 0,
    "Pineapple": 0,
    "Parmesan": 0,
    "Breadcrumbs": 0,
    "No Drizzle": 0,
    "BBQ": 0,
    "Garlic Parmesan": 0,
    "Buffalo": 0,
    "Pesto": 0,
    "Ranch": 0,
    "Hot Honey": 0,
    "No Side": 0,
    "Garlic Bread": 1.99,
    "Cheesy Garlic Bread": 1.99,
    "Cheesecake": 4.99,
    "Large Chocolate Chunk Cookie": 4.99,
    "Doritos": 1.99,
    "Cheetos": 1.99,
    "Lays Barbecue": 1.99,
    "Lays Classic": 1.99,
    "Cheesy Broccoli": 2.99,
    "No Drink": 0,
    "Water Bottle": 1.49,
    "Apple Juice": 2.49,
    "Coke": 1.99,
    "Dr. Pepper": 1.99,
    "Sprite": 1.99,
    "Diet Coke": 1.99,
    "Powerade (Blue Mountain Berry Blast)": 1.99,
    "Minute Maid Lemonade": 1.99
}
folder_path = 'ronis\data\datamonth'
months = ["january", "february", 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
new_files = []
for i in months:
    for n in files:
        if i in n:
            new_files.append(pd.read_csv(n, index_col="Order ID", parse_dates=['Sent Date']))
files = new_files
for i in files:
    i["Date"] = i["Sent Date"].dt.date
    i["Time"] = i["Sent Date"].dt.time
    i["Time Points"] = i['Sent Date'].dt.hour * 3600 + i['Sent Date'].dt.minute * 60 + i['Sent Date'].dt.month * 1000000000+i['Sent Date'].dt.day * 1000000 + i['Sent Date'].dt.second
def additup(months):
    base = months[0]
    for i in range(1, len(months)):
        base = pd.concat([base, months[i]])
    return base
def additup(startRange= '2000-02-28 14:30:00', endRange = '2100-02-28 14:30:00'):
    base = files[0]
    for i in files:
        base = pd.concat([base, i])
    return base[(base['Sent Date'] >= dt.datetime.strptime(startRange, '%Y-%m-%d %H:%M:%S'))|(base['Sent Date'] <= dt.datetime.strptime(endRange, '%Y-%m-%d %H:%M:%S'))]
def group_it_up(df, tip):
    if(tip == "Main"):
        slatty = df[(df["Option Group Name"] == 'Noods') | (df["Option Group Name"] == 'Choose Your Melted Cheese') | (df["Option Group Name"] == 'Mix Bases')]
    elif(tip == "Cheese"):
        slatty = df[(df["Option Group Name"] == "Choose Your " + tip)|(df["Option Group Name"] == "Mix Bases")]
    elif tip == "Mac and Cheese Options":
        slatty = df[(df["Option Group Name"] == "Mac and Cheese Options")]
    else:
        slatty = df[(df["Option Group Name"] == "Choose Your " + tip)]
    return slatty
def howmanyTypes(df, col):
    df2= group_it_up(df, col)
    if(col in ["Meats", "Sides", "Drizzles"]):
        col = col[:-1]
    if(col == 'Cheese'):
        return df2[(df2["Modifier"] != "No " + col)|(df2["Modifier"] != 'MIX')].groupby('Modifier')['Order #'].count().sort_values(ascending = False)
    return df2[(df2["Modifier"] != "No " + col)].groupby('Modifier')['Order #'].count().sort_values(ascending = False)
def weAintGotHours(df):
    df["Hours"] = df["Sent Date"].dt.hour
    df["strhours"] = df["Sent Date"].dt.strftime("%I %p")
    return df.groupby("strhours")["Order #"].count()
def weAintGotMonths(df):
    df["Month"] = df["Sent Date"].dt.month
    return df.groupby("Month")["Order #"].count()
def increments(df, hours=0, minutes=0, seconds=1):
    inc = hours*3600+minutes*60+seconds
    df["Increments"] = df["Time Points"]//inc
    if(hours != 0):
        df['Why'] = ((df["Sent Date"].dt.hour//hours)*hours).astype(str)
        df["IncTime"] = df["Why"]+":00:00"
    elif(minutes != 0):
        df['Why'] = ((df["Sent Date"].dt.minute//minutes)*minutes).astype(str)
        df["IncTime"] = df["Sent Date"].dt.hour.astype(str)+":"+df["Why"]+":00"
    elif(seconds != 0):
        df['Why'] = ((df["Sent Date"].dt.second//seconds)*seconds).astype(str)
        df["IncTime"] = str(df["Sent Date"].dt.hour)+str(df["Sent Date"].dt.minute)+str(df["Sent Date"].dt.second)
    return df
def prices(df):
    rows = []
    d = {}
    prices = pd.read_csv("ronis\data\ItemData.csv")
    for index, row in df.iterrows():
        
        if(row["Option Group Name"] == "Noods" or row["Option Group Name"] == "Choose Your Melted Cheese"):
            
            if d != {}:
                d["Price"] = round(d["Price"] *1.0625,2)
                rows.append(d)
            
            d = row[['Order #', 'Sent Date', 'Modifier', 'Parent Menu Selection']].to_dict()
            
            d["Toppings"] = []
            d["Drink"] = []
            d["Side"] = []
            d["Meats"] = []
            d["Cheese"] = []
            d["Drizzles"] = []
            d["Do you want Mac and Cheese added inside?"] = False
            d["Price"] = 8.99
            
        else:
            try:
                if(row["Option Group Name"] == "Do you want Mac and Cheese added inside?"):
                    d["Do you want Mac and Cheese added inside?"] = True
                else:
                    d[row["Option Group Name"].split()[-1]].append(row['Modifier'])
                    d['Price'] += price[row['Modifier']]
            except:
                pass
    return pd.DataFrame(rows) 
print(howmanyTypes(additup(), "Mac and Cheese Options"))

