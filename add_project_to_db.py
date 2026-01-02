import shared

connection = shared.connectDb()
cursor = connection.cursor()
print(f"What do you want to use for the case number? ", end="")
number = input()
newProject = '{"id":1,"customer":"/web/v1/customer/6666940/","customer_id":"6666940","number":"' + number + '","name":"Example ' + number + '","file_upload_required":false,"active":false,"notes":"these are my notes"}'
rv = shared.runSql(cursor, f"INSERT INTO {shared.MAIN_TABLE} SELECT * FROM json_populate_record(NULL::{shared.MAIN_TABLE}, '{newProject}') RETURNING *;")
if rv:
    print(rv)
    print("Project NOT Inserted")
else:
    print("Project Inserted")