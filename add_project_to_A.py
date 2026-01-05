import shared
import main

print("What do you want to use for the case number? ", end="")
number = input()

new_project = {
    "customer":"/web/v1/customer/6666940/",
    "customer_id":"6666940",
    "number":number,
    "name":f"Example {number}",
    "notes":"these are my notes"
}

connection = shared.connectDb()
cursor = connection.cursor()
rv = main.addToIntempus(cursor, )
connection.close()

if rv:
    print(rv)
    print("Project NOT Added")
else:
    print("Project Added")