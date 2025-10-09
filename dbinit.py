import sqlite3

conn = sqlite3.connect('alltimes.db')

cursor = conn.cursor()

table_query = "CREATE TABLE IF NOT EXISTS timelog (time_type TEXT, date TEXT, elapsed REAL)"

cursor.execute(table_query)