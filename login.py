import requests
import json

import mysqlHandler

mysqlUser = [""]
mysqlPassword = [""]
username = [""]
password = [""]

def checkSession():
    try:
        with open('configs/cache.json', "r") as openfile:
            json_object = json.load(openfile)
            username[0] = json_object["username"]
            password[0] = json_object["password"]
    except:
        return

    url = "https://scheibenwischer.racing/login/requestAppLogin.php"
    obj = {'user': username[0], 'password': password[0]}
    answer = requests.post(url, data=obj)
    answerJson = answer.json()

    if answerJson["mysqlName"] != "":
        mysqlUser[0] = answerJson["mysqlName"]
        mysqlPassword[0] = answerJson["mysqlPassword"]
        mysqlHandler.createConnection(getMysqlUser(), getMySqlPassword())
        return True


def checkLogin(username, password, isChecked):
    url = "https://scheibenwischer.racing/login/requestAppLogin.php"
    obj = {'user': username, 'password': password}
    answer = requests.post(url, data=obj)
    answerJson = answer.json()

    if answerJson["mysqlName"] != "":
        if isChecked:
            dictonaryCache = {
                'username': username,
                'password': password
            }

            with open("configs/cache.json", "w") as outfile:
                json.dump(dictonaryCache, outfile)
        mysqlUser[0] = answerJson["mysqlName"]
        mysqlPassword[0] = answerJson["mysqlPassword"]
        mysqlHandler.createConnection(getMysqlUser(), getMySqlPassword())
        username[0]=username
        return True


def getMysqlUser():
    return mysqlUser[0]


def getMySqlPassword():
    return mysqlPassword[0]


def getUsername():
    return username[0]

def getPassword():
    return password[0]
