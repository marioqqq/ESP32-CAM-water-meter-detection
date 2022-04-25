from datetime import datetime
import mysql.connector

mydb = mysql.connector.connect(
    host="192.168.100.11",
    user="bakalarka",
    password="raspberry",
    database="home2")
mycursor = mydb.cursor()

stop = False
control = 0


def read_values(table):
    mycursor.execute(f"SELECT * FROM {table} ORDER BY time DESC LIMIT 1")
    myresult = mycursor.fetchall()
    if table == "new":
        try:
            val = myresult[0][1]
            val1 = float(val)
        except ValueError:
            return val, True
        except IndexError:
            return val, True
        else:
            return val1, False
    else:
        return myresult[0][1]


def open_values(path):
    with open(path) as f:
        val = f.readlines()
    try:
        val1 = float(val[0])
    except ValueError:
        return val, True
    except IndexError:
        return val, True
    else:
        return val1, False


def sql_database(measurement, value):
    finaldb = (f"INSERT INTO {measurement} (value) VALUES ({value})")
    mycursor.execute(finaldb)
    mydb.commit()


if __name__ == "__main__":
    val1, stop = read_values("new")
    val2 = read_values("old")
    val3 = read_values("final")

    if not stop:
        control = val3
        if (val1 > val2):
            value = val3 + (val1 - val2)
        elif (val1 < val2):
            value = val3 - val2 + 1000 + val1
        else:
            value = val3

        if (control+100) > value:
            sql_database("old", int(val1))
            sql_database("final", int(value))
        else:
            sql_database("final", int(val3))

    else:
        sql_database("final", int(val3))
