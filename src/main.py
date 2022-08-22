
import json
from app import app

with open("config.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

firstName = jsonObject["firstName"]
lastName = jsonObject["lastName"]

if firstName == "" and lastName == "":
    print("It seems like you're a new user. What is your name?")
    firstName = input("First Name: ")
    lastName = input("Last Name: ")
    jsonData = {
        "firstName": firstName,
        "lastName": lastName
    }
    with open('config.json', 'w') as jsonFile:
        json.dump(jsonData, jsonFile)
        jsonFile.close()
else:
    print(f"Welcome back, {firstName} {lastName}!")
exec(open('index.py').read())

app.run_server(debug=False, port=8000, dev_tools_silence_routes_logging=True,use_reloader=False)
