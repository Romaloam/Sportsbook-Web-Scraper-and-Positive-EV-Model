from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime,time,timedelta
import csv
import pandas as pd
import sqlite3

def isHandicap(obj):
    verdict=bool
    if 4<=len(obj)<=5 and ("+" in obj or "-" in obj) and "." in obj:
        verdict=True
    else:
        verdict=False
    return verdict

def isLine(obj):
    verdict=bool
    if 5<=len(obj)<=6 and "." in obj:
        verdict=True
    else:
        verdict=False
    return verdict

def isTotal(obj):
    verdict=bool
    if 2<=len(obj)<=4 and "+" not in obj and "-" not in obj:
        verdict=True
    else:
        verdict=False
    return verdict

def isOther(obj):
    verdict=bool
    if 2<=len(obj)<=4 and "+" in obj and "." not in obj:
        verdict=True
    else:
        verdict=False
    return verdict
    
    

#Init
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

#Open Page
url = "https://www.pinnacle.com/en/baseball/matchups/"
driver.get(url)
driver.set_window_size(2048, 2048) 

#Timer
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div[1]/div[2]/main/div/div[2]/div/div')))

#Get data
data = driver.find_elements(By.XPATH,'//*[@id="root"]/div[1]/div[2]/main/div/div[2]/div/div')


#Uniform dates
i=0
date=''
while i< len(data):
    if data[i].text.isupper() and "+" not in data[i].text:
        if "2026" in data[i].text:
            date=data[i].text
        elif "TODAY" in data[i].text:
            date=datetime.now().strftime("%a, %b %d, %Y").upper()
        elif "TOMORROW" in data[i].text:
            date=(datetime.now()+timedelta(days=1)).strftime("%a, %b %d, %Y").upper()
        else:
            pass
        del(data[i])
    else:
        #Parse
        data[i]=data[i].text.split("\n")
        data[i].insert(0,date)
        i+=1
titles=["Dates","Home","Away","Time","HomeMoneyline","AwayMoneyline","HomeHandicap","HomeHandicapLine","AwayHandicap","AwayHandicapLine","Over","OverLine","Under","UnderLine","Other"]

for q in data: #Fill empty data
    if len(q)<15:
        if (isLine(q[4]) and isLine(q[5]))==False:
            q.insert(4,"")
            q.insert(5,"")
        else:
            pass
        
        if (isHandicap(q[6]) and isLine(q[7]) and isHandicap(q[8]) and isLine(q[9]))==False:
            q.insert(6,"")
            q.insert(7,"")
            q.insert(8,"")
            q.insert(9,"")
        else:
            pass
        

        if (isTotal(q[10]) and isLine(q[11]) and isTotal(q[12]) and isLine(q[13]))==False:
            q.insert(10,"")
            q.insert(11,"")
            q.insert(12,"")
            q.insert(13,"")
        else:
            pass

        if (len(q))<15:
            q.append("")
        else:
            pass
    else:
        pass


#Turn to dictionary for pandas       
cleanData={}
j=0
for item in titles:
    temp=[]
    for thang in data:
        temp.append(thang[j])
    j+=1
    cleanData[f"{item}"]=temp

#CloseWebDriver
driver.quit()

#Database
df = pd.DataFrame(cleanData,index=range(1,len(cleanData["Dates"])+1))

#output Excel file
xlsx_file_path = '/Users/romantestani/Desktop/OddsScrape.xlsx'

#Write the DataFrame to an Excel file
df.to_excel(xlsx_file_path, engine='openpyxl')

#SQL
conn = sqlite3.connect('baseball_odds.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS odds_history (
    curr TEXT,
    date TEXT,
    home TEXT,
    away TEXT,
    time TEXT,
    homeMoneyline TEXT,
    awayMoneyline TEXT,
    homeHandicap TEXT,
    homeHandicapLine TEXT,
    awayHandicap TEXT,
    awayHandicapLine TEXT,
    over TEXT,
    overLine TEXT,
    under TEXT,
    underLine TEXT,
    other TEXT

)''')
conn.commit()

#Insert data into SQL database
for b in data:
    curr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT INTO odds_history (curr,date,home,away,time,homeMoneyline,awayMoneyline,homeHandicap,homeHandicapLine,awayHandicap,awayHandicapLine,over,overLine,under,underLine,other) 
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', 
               (curr,b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10],b[11],b[12],b[13],b[14]))
#Save
conn.commit()

#Print SQL table
c.execute('SELECT * FROM odds_history')
rows = c.fetchall()
for row in rows:
    print(row)

conn.close()

###Print table formatting
##c.execute("PRAGMA table_info(odds_history);")
##columns = c.fetchall()
##
##for column in columns:
##    print(column)
##
##conn.close()
