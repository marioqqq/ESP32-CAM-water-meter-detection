import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
host="192.168.100.11",
user="bakalarka",
password="raspberry",
database="home2")
mycursor = mydb.cursor()

def get_data():
    df = pd.read_excel("/home/pi/shared/main2/statistics/statistics.xlsx")
    row = df.index[-1] + 3
    accuracy_true = 0
    accuracy_false = 0
    accuracy_total = 0
    for i in range(row):
        if i != 0:
            if i == row-2:
                break
            if df.loc[i,"Status"] is True:
                accuracy_true += 1
            elif df.loc[i,"Status"] is False:
                accuracy_false += 1

    total = accuracy_true + accuracy_false
    if total != 0:
        accuracy_total = round((accuracy_true/(total)) * 100,2)
    else:
        accuracy_total = 0
    return accuracy_true,accuracy_false,total,accuracy_total

def sql_database (accuracy_true,accuracy_false,total,accuracy_total):
    finaldb = (f"INSERT INTO accuracy (accurate,inaccurate,total,accuracy) VALUES ({accuracy_true},{accuracy_false},{total},{accuracy_total})")
    mycursor.execute(finaldb)
    mydb.commit()

if __name__ == "__main__":
    accuracy_true,accuracy_false,total,accuracy_total = get_data()
    sql_database(accuracy_true,accuracy_false,total,accuracy_total)