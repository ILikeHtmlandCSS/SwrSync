import json
import os
import sys
import math
import customtkinter
import time
import threading
import autoSync
import mysqlHandler
from login import checkLogin
from login import checkSession
import tkinter
from pathlib import Path
from PIL import Image
import schedule


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("configs/color.json")

carSettingsCfg = Path("configs/carSettings.json")
carSettingsCfg.touch()

setupSettingsCfg = Path("configs/setupSettings.json")
setupSettingsCfg.touch()

intervalCfg = Path("configs/intervalSettings.json")
intervalCfg.touch()

root = customtkinter.CTk(fg_color="#3a3e41")
root.geometry("1280x720")
root.resizable(False, False)
root.title("SWR-Sync")
root.wm_iconbitmap("images/SWR.ico")

root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)

root.grid_columnconfigure((1, 0), weight=0)
root.grid_columnconfigure((0, 1), weight=0)
root.grid_columnconfigure((1, 1), weight=1)


def loadPanel(panelId):
    if loadedPanel is not None:
        curPanel = loadedPanel[0]
        loadedPanel[0] = None
        curPanel.pack_forget()
    panel = panels[panelId]
    loadedPanel[0] = panel
    panel.pack(pady=10)


def validate_entry_text(new_text, id):
    if not new_text:
        return True
    try:
        float(new_text)
        raceLength = raceLenghtEntry.get()
        lapTimeMin = lapTimeMinEntry.get()
        lapTimeSec = lapTimeSecEntry.get()
        lapTimeMil = lapTimeMilEntry.get()
        fuelCon = fuelEntry.get()

        match id:
            case "0":
                raceLength = new_text
            case "1":
                lapTimeMin = new_text
            case "2":
                lapTimeSec = new_text
            case "3":
                lapTimeMil = new_text
            case "4":
                fuelCon = new_text

        lapTimeInMin = 0
        lapTimeSecToMin = [0]
        lapTimeMilToMin = [0]
        if raceLength == "" or raceLength == "0":
            totalLaps = 0
            totalLapsValue.configure(text=0)
            minFuelValue.configure(text=0)
            return True
        if lapTimeMin == "" or lapTimeMin == "0":
            totalLapsValue.configure(text=0)
            minFuelValue.configure(text=0)
            return True
        if lapTimeSec == "":
            lapTimeSec = 0
        if lapTimeMil == "":
            lapTimeMil = 0
        if fuelCon == "" or fuelCon == "0":
            totalLapsValue.configure(text=0)
            minFuelValue.configure(text=0)
            fuelCon = 0

        lapTimeInMin = lapTimeMin
        lapTimeSecToMin[0] = int(lapTimeSec) / 60
        lapTimeMilToMin[0] = int(lapTimeMil)//60000

        lapTimeInMin = int(lapTimeInMin)+lapTimeSecToMin[0]+lapTimeMilToMin[0]
        totalLaps = math.ceil(int(raceLength)/lapTimeInMin)
        totalLapsValue.configure(text=totalLaps)

        print(totalLaps)
        minFuel = math.ceil((int(totalLaps) * float(fuelCon))+1)
        minFuelValue.configure(text=minFuel)
        safeFuel = math.ceil(minFuel+(2*float(fuelCon)))
        safeFuelValue.configure(text=safeFuel)
        recommendedFuel = math.ceil((int(minFuel)+(int(minFuel)+1+float(fuelCon)))/2)
        recommendedFuelValue.configure(text=recommendedFuel)




        return True
    except ValueError:
        return False

validate_cmd = root.register(validate_entry_text)


def loginUser(username, password, boolRemember):
    if checkLogin(username, password, boolRemember):
        loginFrame.destroy()
        topBar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        navBar.grid(row=1, column=0, sticky="nsw")
        content.grid(row=1, column=1, sticky="nsew")
        getInterval()
        loadCars()
        loadPanel(0)


loginFrame = customtkinter.CTkFrame(master=root, corner_radius=0)
loginFrame.place(relx=0.5, rely=0.5, anchor="c")

entry1 = customtkinter.CTkEntry(master=loginFrame, placeholder_text="  username", font=('Roboto', 14), width=300,
                                height=50, corner_radius=0, bg_color="#4e5256", fg_color="#4e5256",
                                border_color="#4e5256")
entry1.pack(pady=(45, 0), padx=45)

entry2 = customtkinter.CTkEntry(master=loginFrame, placeholder_text="  password", show="*", font=('Roboto', 14),
                                height=50, width=300, corner_radius=0)
entry2.pack(pady=15, padx=10)

button = customtkinter.CTkButton(master=loginFrame, text="SIGN IN",
                                 command=lambda: loginUser(entry1.get(), entry2.get(), checkbox.get()),
                                 font=('Roboto', 14),
                                 height=50,
                                 width=300, corner_radius=0)
button.pack()

checkbox = customtkinter.CTkCheckBox(master=loginFrame, text="Remember me", font=('Roboto', 18))
checkbox.pack(pady=(22.5, 22.5))

topBar = customtkinter.CTkFrame(master=root, corner_radius=0, fg_color="#292c2e", height=70)



# navbar
navBar = customtkinter.CTkFrame(master=root, corner_radius=0, fg_color="#3a3e41", width=330)

syncPanelBtn = customtkinter.CTkButton(master=navBar, width=300, text="Synchronisierung", image=customtkinter.CTkImage(light_image=Image.open("images/rotate-solid.png"), size=(22, 22)), fg_color="#3a3e41", font=('Roboto', 18, 'bold'), corner_radius=0, text_color="#d3bbb0", hover_color="#26292b", anchor="w", border_spacing=10, command=lambda: loadPanel(0))
syncPanelBtn.pack(pady=(10, 0))

fuelCalcBtn = customtkinter.CTkButton(master=navBar, width=300, text="Sprit-Rechner", image=customtkinter.CTkImage(light_image=Image.open("images/gas-pump-solid.png"), size=(22, 22)), fg_color="#3a3e41", font=('Roboto', 18, 'bold'), corner_radius=0, text_color="#d3bbb0", hover_color="#26292b", anchor="w", border_spacing=10, command=lambda: loadPanel(1))
fuelCalcBtn.pack(pady=(10, 0))

stintPtn = customtkinter.CTkButton(master=navBar, width=300, text="Stints", image=customtkinter.CTkImage(light_image=Image.open("images/list-solid.png"), size=(22, 22)), fg_color="#3a3e41", font=('Roboto', 18, 'bold'), corner_radius=0, text_color="#d3bbb0", hover_color="#26292b", anchor="w", border_spacing=10, command=lambda: loadPanel(2))
stintPtn.pack(pady=(10, 0))

#uploadPanelBtn = customtkinter.CTkButton(master=navBar, width=300, text="Livery Upload", image=customtkinter.CTkImage(light_image=Image.open("images/upload-solid.png"), size=(22, 22)), fg_color="#3a3e41", font=('Roboto', 18, 'bold'), corner_radius=0, text_color="#d3bbb0", hover_color="#26292b", anchor="w", border_spacing=10)
#uploadPanelBtn.pack(pady=(10, 0))

content = customtkinter.CTkFrame(master=root, corner_radius=0, fg_color="#2d2f32")

panels = {int(): customtkinter.CTkCheckBox(master=None)}

syncFrame = customtkinter.CTkFrame(master=content, corner_radius=0, fg_color="#2d2f32")
syncFrame.grid_columnconfigure((0, 0), weight=1)
panels[0] = syncFrame

teamFrame = customtkinter.CTkFrame(master=content, corner_radius=0, fg_color="#2d2f32")

fuelFrame = customtkinter.CTkFrame(master=teamFrame, corner_radius=0, fg_color="#2d2f32")

raceLengtText = customtkinter.CTkLabel(master=fuelFrame, corner_radius=0, text="Race length (in minutes)", font=('Roboto', 20), fg_color="#2d2f32", text_color="#d5bba4")
raceLengtText.pack()
raceLenghtEntry = customtkinter.CTkEntry(master=fuelFrame, corner_radius=2, placeholder_text="Race length in minutes (e.g. 20)", fg_color="#232327", border_color="#232327", width=650, height=50, font=('Roboto', 18), justify="center", text_color="#E76D83", placeholder_text_color="#8ca3af")
raceLenghtEntry.configure(validate="key", validatecommand=(validate_cmd, "%P", 0))
raceLenghtEntry.pack(pady=10)

lapTimeFrame = customtkinter.CTkFrame(master=fuelFrame, corner_radius=0, fg_color="#2d2f32")
lapTimeFrame.pack(pady=(20,0))
lapTimeText = customtkinter.CTkLabel(master=lapTimeFrame, corner_radius=0, text="Lap time", font=('Roboto', 20), fg_color="#2d2f32", text_color="#d5bba4")
lapTimeText.grid(row=0, column=0, columnspan=3)
lapTimeMinEntry = customtkinter.CTkEntry(master=lapTimeFrame, corner_radius=2, placeholder_text="Min", fg_color="#232327", border_color="#232327", width=210, height=50, font=('Roboto', 18), justify="center", placeholder_text_color="#8ca3af", text_color="#E76D83")
lapTimeMinEntry.configure(validate="key", validatecommand=(validate_cmd, "%P", 1))
lapTimeMinEntry.grid(row=1, column=0, padx=5, pady=(5, 0))
lapTimeSecEntry = customtkinter.CTkEntry(master=lapTimeFrame, corner_radius=2, placeholder_text="Sec", fg_color="#232327", border_color="#232327", width=210, height=50, font=('Roboto', 18), justify="center", placeholder_text_color="#8ca3af", text_color="#E76D83")
lapTimeSecEntry.configure(validate="key", validatecommand=(validate_cmd, "%P", 2))
lapTimeSecEntry.grid(row=1, column=1, padx=5, pady=(5, 0))
lapTimeMilEntry = customtkinter.CTkEntry(master=lapTimeFrame, corner_radius=2, placeholder_text="Ms", fg_color="#232327", border_color="#232327", width=210, height=50, font=('Roboto', 18), justify="center", placeholder_text_color="#8ca3af", text_color="#E76D83")
lapTimeMilEntry.configure(validate="key", validatecommand=(validate_cmd, "%P", 3))
lapTimeMilEntry.grid(row=1, column=2, padx=5, pady=(5, 0))
lapTimeInfoText = customtkinter.CTkLabel(master=lapTimeFrame, corner_radius=0, text="Min. Sec : Ms - *You don't need to fill milliseconds.", font=('Roboto', 10, 'bold'), fg_color="#2d2f32", text_color="#E76D83")
lapTimeInfoText.grid(row=3, column=0, columnspan=3)

fuelText = customtkinter.CTkLabel(master=fuelFrame, corner_radius=0, text="Fuel per lap", font=('Roboto', 20), fg_color="#2d2f32", text_color="#d5bba4")
fuelText.pack(pady=(20,0))
fuelEntry = customtkinter.CTkEntry(master=fuelFrame, corner_radius=2, placeholder_text="Fuel consumption per lap (e.g. 3.7)", fg_color="#232327", border_color="#232327", width=650, height=50, font=('Roboto', 18), justify="center", placeholder_text_color="#8ca3af", text_color="#E76D83")
fuelEntry.configure(validate="key", validatecommand=(validate_cmd, "%P", 4))
fuelEntry.pack(pady=(5, 0))

smallTipFrame = customtkinter.CTkFrame(master=fuelFrame, corner_radius=0, fg_color="#2d2f32")
smallTipFrame.pack(pady=(20,0))

totalLapsFrame = customtkinter.CTkFrame(master=smallTipFrame, corner_radius=0, fg_color="#2d2f32")
totalLapsFrame.grid(row=0, column=0, padx=10)
totalLapsText = customtkinter.CTkLabel(master=totalLapsFrame, corner_radius=0, text="Total Laps", font=('Roboto', 15), fg_color="#2d2f32", text_color="#9A9A9A")
totalLapsText.pack()
totalLapsValue = customtkinter.CTkLabel(master=totalLapsFrame, corner_radius=0, text="0", font=('Roboto', 15), fg_color="#2d2f32", text_color="#9A9A9A")
totalLapsValue.pack(anchor="center")

minFuelFrame = customtkinter.CTkFrame(master=smallTipFrame, corner_radius=0, fg_color="#2d2f32")
minFuelFrame.grid(row=0, column=1, padx=10)
mineFuelText = customtkinter.CTkLabel(master=minFuelFrame, corner_radius=0, text="Minimum Fuel", font=('Roboto', 15), fg_color="#2d2f32", text_color="#9A9A9A")
mineFuelText.pack()
minFuelValue = customtkinter.CTkLabel(master=minFuelFrame, corner_radius=0, text="0", font=('Roboto', 15), fg_color="#2d2f32", text_color="#9A9A9A")
minFuelValue.pack(anchor="center")

safeFuelFrame = customtkinter.CTkFrame(master=fuelFrame, corner_radius=2, fg_color="#161719")
safeFuelFrame.pack(pady=(20,0))
safeFuelText = customtkinter.CTkLabel(master=safeFuelFrame, corner_radius=0, text="Safe (Full formation lap)", font=('Roboto', 15), fg_color="#161719", text_color="#9A9A9A", width=630)
safeFuelText.pack(pady=(10, 0))
safeFuelValue = customtkinter.CTkLabel(master=safeFuelFrame, corner_radius=0, text="0", font=('Roboto', 15), fg_color="#161719", text_color="#9A9A9A")
safeFuelValue.pack(pady=(0, 10))

recommendedFuelFrame = customtkinter.CTkFrame(master=fuelFrame, corner_radius=2, fg_color="#0d0e0f")
recommendedFuelFrame.pack()
recommendedFuelText = customtkinter.CTkLabel(master=recommendedFuelFrame, corner_radius=0, text="Recommended", font=('Roboto', 20, 'bold'), fg_color="#0d0e0f", text_color="#E76D83", width=630)
recommendedFuelText.pack(pady=(25, 0))
recommendedFuelValue = customtkinter.CTkLabel(master=recommendedFuelFrame, corner_radius=0, text="0", font=('Roboto', 25, 'bold'), fg_color="#0d0e0f", text_color="#fff")
recommendedFuelValue.pack(pady=(5, 25))

fuelFrame.pack()



panels[1] = teamFrame

carBox = customtkinter.CTkFrame(master=syncFrame, corner_radius=0, fg_color="#2d2f32")
carBox.grid_columnconfigure((0, 0), weight=1)
carBox.grid(row=0, column=0)

carBoxes = {int(): customtkinter.CTkCheckBox(master=None)}
setupCheckmarks = {int(): customtkinter.CTkCheckBox(master=None)}

loadedPanel = [customtkinter.CTkFrame(master=None)]


def setInterval(interval, entry):
    if not interval.isnumeric():
        entry.configure(text="Use Numbers!")
        return

    with open("configs/intervalSettings.json", "r+") as file:
        intSettings = []
        intSettings.append(int(interval))
        file.seek(0)
        file.truncate(0)
        json.dump(intSettings, file)

    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

def getInterval():
    with open("configs/intervalSettings.json", "r+") as file:
        if os.path.getsize('configs/intervalSettings.json') == 0:
            intSettings = []
            intSettings.append(5)
            json.dump(intSettings, file)
            return 5

        json_obj = json.load(file)
        return json_obj[0]


def openInterval():
    intervalWindow = customtkinter.CTkToplevel(fg_color="#3a3e41")
    intervalWindow.geometry("300x300")
    intervalWindow.resizable(False, False)
    intervalWindow.title("Set Interval")

    intervalFrame = customtkinter.CTkFrame(master=intervalWindow, fg_color="#3a3e41")
    intervalFrame.place(relx=.5, rely=.5, anchor="center")
    intervalValue = tkinter.StringVar(intervalFrame, getInterval())
    intervalEntry = customtkinter.CTkEntry(master=intervalFrame, font=('Roboto', 14), textvariable=intervalValue, height=30, width=30)
    intervalEntry.configure(validate="key", validatecommand=(validate_cmd, "%P"))
    intervalEntry.grid(row=0, column=0)
    intervalLabel = customtkinter.CTkLabel(master=intervalFrame, font=('Roboto', 14), height=30, text="Set Interval (minutes)")
    intervalLabel.grid(row=0, column=1, padx=10)
    intervalButton = customtkinter.CTkButton(master=intervalFrame, height=30, text="Save", command=lambda: setInterval(intervalEntry.get(), intervalButton))
    intervalButton.grid(row=1, column=0, columnspan=2, pady=10)


def loadCars():
    cursor = mysqlHandler.getCursor()
    cursor.execute("SELECT DISTINCT car FROM setups ORDER BY car")
    cars = cursor.fetchall()

    with open("configs/carSettings.json", "r+") as file:
        if os.path.getsize('configs/carSettings.json') == 0:
            carDict = {}
            for x in range(len(cars)):
                carDict[str(x)] = 0
            print(carDict)
            json.dump(carDict, file)

    with open("configs/setupSettings.json", "r+") as file:
        if os.path.getsize('configs/setupSettings.json') == 0:
            setupDict = {}
            for x in range(6):
                setupDict[str(x)] = 0
            print(setupDict)
            json.dump(setupDict, file)

    with open("configs/carSettings.json", "r") as file:
        json_obj = json.load(file)
        for x in range(len(cars)):
            carValue = tkinter.IntVar(value=json_obj[str(x)])
            car = customtkinter.CTkCheckBox(master=carBox, text=cars[x], font=('Roboto', 16), width=500, checkbox_height=25, checkbox_width=25, corner_radius=6, command=lambda x=x: carCheckBoxClicked(x), variable=carValue)
            car.grid(row=x, column=0, columnspan=1, padx=20, pady=2)
            carBoxes.__setitem__(x, car)

    with open("configs/setupSettings.json", "r") as file:
        json_obj = json.load(file)
        for x in range(len(json_obj)):
            checkmarkValue = tkinter.IntVar(value=json_obj[str(x)])
            if x == 0:
                checkmark = customtkinter.CTkCheckBox(master=carBox, text="GoSetup", font=('Roboto', 16), width=500,
                                                checkbox_height=25, checkbox_width=25, corner_radius=6,
                                                command=lambda x=x: setupCheckboxClicked(x), variable=checkmarkValue)
                checkmark.grid(row=x, column=1, columnspan=1, padx=20, pady=2)
                setupCheckmarks.__setitem__(x, checkmark)
            elif x == 1:
                checkmark = customtkinter.CTkCheckBox(master=carBox, text="CDA", font=('Roboto', 16), width=500,
                                                checkbox_height=25, checkbox_width=25, corner_radius=6,
                                                command=lambda x=x: setupCheckboxClicked(x), variable=checkmarkValue)
                checkmark.grid(row=x, column=1, columnspan=1, padx=20, pady=2)
                setupCheckmarks.__setitem__(x, checkmark)
            elif x == 2:
                checkmark = customtkinter.CTkCheckBox(master=carBox, text="Rennwelten", font=('Roboto', 16), width=500,
                                                checkbox_height=25, checkbox_width=25, corner_radius=6,
                                                command=lambda x=x: setupCheckboxClicked(x), variable=checkmarkValue)
                checkmark.grid(row=x, column=1, columnspan=1, padx=20, pady=2)
                setupCheckmarks.__setitem__(x, checkmark)
            elif x == 3:
                checkmark = customtkinter.CTkCheckBox(master=carBox, text="Sync Setups", font=('Roboto', 16), width=500,
                                                      checkbox_height=25, checkbox_width=25, corner_radius=6,
                                                      command=lambda x=x: setupCheckboxClicked(x),
                                                      variable=checkmarkValue)
                checkmark.grid(row=x+1, column=1, columnspan=1, padx=20, pady=2)
                setupCheckmarks.__setitem__(x, checkmark)
            elif x == 5:
                checkmark = customtkinter.CTkButton(master=carBox, text="Interval", font=('Roboto', 16), width=150,
                                                      height=25, corner_radius=6, command=lambda: openInterval())
                checkmark.grid(row=x, column=1, columnspan=1, padx=20, pady=2, sticky="W")
                setupCheckmarks.__setitem__(x, checkmark)


def carCheckBoxClicked(checkboxId):
    checkbox = carBoxes[checkboxId]
    with open("configs/carSettings.json", "r+") as file:
        json_obj = json.load(file)
        json_obj[str(checkboxId)] = checkbox.get()
        file.seek(0)
        file.truncate(0)
        json.dump(json_obj, file)


def setupCheckboxClicked(setupID):
    checkbox = setupCheckmarks[setupID]
    with open("configs/setupSettings.json", "r+") as file:
        json_obj = json.load(file)
        json_obj[str(setupID)] = checkbox.get()
        file.seek(0)
        file.truncate(0)
        json.dump(json_obj, file)


if checkSession():
    loginFrame.destroy()
    topBar.grid(row=0, column=0, columnspan=2, sticky="nsew")
    navBar.grid(row=1, column=0, sticky="nsw")
    content.grid(row=1, column=1, sticky="nsew")
    getInterval()
    loadCars()
    loadPanel(0)


def init_sync():
    autoSync.sync()
    schedule.every(getInterval()).minutes.do(autoSync.sync)

    while True:
        schedule.run_pending()
        time.sleep(0)

sync_thread = threading.Thread(target=init_sync)
sync_thread.setDaemon(True)
sync_thread.start()

root.mainloop()
