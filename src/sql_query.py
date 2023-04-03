import sqlite3

# Connect to the SQL dump file
conn = sqlite3.connect("../adw_nepal-20230221.sql")

# Create a cursor object
cur = conn.cursor()

# Execute the query for a specific keyword
# keyword = "akṣara"
# cur.execute("SELECT * FROM baskets WHERE column LIKE ?", ("%" + keyword + "%",))


# Fetch the results and print them
# results = cur.fetchall()
# for row in results:
# print(row)

# Get a list of all the table names in the database
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()


# Print the table names
for table in tables:
    print(table[0])


# Close the cursor and the connection
cur.close()
conn.close()
