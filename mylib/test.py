from databricks import sql
import os

connection = sql.connect(
                        server_hostname = "adb-7849422577987932.12.azuredatabricks.net",
                        http_path = "/sql/1.0/warehouses/32b35d44cdf2d795",
                        access_token = "<access-token>")

cursor = connection.cursor()

cursor.execute("SELECT * from range(10)")
print(cursor.fetchall())

cursor.close()
connection.close()