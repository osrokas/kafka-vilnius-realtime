from trino.dbapi import connect

conn = connect(
    host='localhost',
    port=8080,
    user='trino',
    catalog='iceberg',
    schema='silver'
)

cursor = conn.cursor()

# Query Iceberg table
cursor.execute("SELECT * FROM gps_data LIMIT 10")
results = cursor.fetchall()

for row in results:
    print(row)

# Get table metadata
cursor.execute("SELECT * FROM \"gps_data$snapshots\"")
snapshots = cursor.fetchall()
print("Snapshots:", snapshots)

conn.close()