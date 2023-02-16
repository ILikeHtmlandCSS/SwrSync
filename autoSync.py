import requests
import os
import mysqlHandler
import json
from multiprocessing.pool import ThreadPool as Pool

syncSetup = [bool]
cars = []
setupTypes = []


def downloadSetups(xCars, yResult):
    if setupTypes.count(yResult[2]):
        setupDict = str(yResult[0])

        if not os.path.exists(os.path.expanduser("~") + "/Documents/Test/Setups/" + xCars[0] + "/" + yResult[3]):
            os.makedirs(os.path.expanduser("~") + "/Documents/Test/Setups/" + xCars[0] + "/" + yResult[3])

        if not os.path.exists(
                os.path.expanduser("~") + "/Documents/Test/Setups/" + xCars[0] + "/" + yResult[3] + "/" + yResult[1]):
            r = requests.get(
                "https://scheibenwischer.racing/requestSetupFile.php?sName=" + setupDict.split("/")[1])

            with open(os.path.expanduser("~") + "/Documents/Test/Setups/" + xCars[0] + "/" + yResult[3] + "/" + yResult[
                1],
                      'wb') as out_file:
                out_file.write(r.content)


pool = Pool(300)
task = []


def stop():
    task[0].cancel()


def sync():
    cursor = mysqlHandler.getCursor()
    cursor.execute("SELECT DISTINCT car FROM setups ORDER BY car")
    allCars = cursor.fetchall()
    cars.clear()
    setupTypes.clear()
    print("Syncing...")
    with open("configs/setupSettings.json", "r") as file:
        json_obj = json.load(file)
        setupTypes.append(0)
        for x in json_obj:
            if x == "4" or x == "5":
                break
            if x == "3":
                if json_obj[x] == 0:
                    syncSetup[0] = False
                break
            if json_obj[x] == 1:
                setupTypes.append(int(x) + 1)

    if not syncSetup[0]:
        return
    with open("configs/carSettings.json", "r") as file:
        json_obj = json.load(file)
        for x in json_obj:
            if json_obj[x] == 1:
                cars.append(allCars[int(x)])

        for x in cars:
            cursor.execute("SELECT fileDirectory, fileName, setupType, track FROM setups WHERE car='" + str(x[0]) + "'")
            result = cursor.fetchall()

            for y in result:
                pool.apply_async(downloadSetups, (x, y))
