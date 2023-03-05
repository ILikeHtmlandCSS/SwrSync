import mysqlHandler


def teamHasStint(user):
    cursor = mysqlHandler.getCursor()
    cursor.execute("SELECT cceTeam FROM userAccounts WHERE userName='" + user + "'")
    teamName = cursor.fetchone()
    cursor.execute("SELECT * FROM stints WHERE teamName='" + teamName[0] + "'")
    teamStint = cursor.fetchall()
    if len(teamStint) == 0:
        createStint(user, 120, 30, 14, 30)


def createStint(user, raceLength, stintLength, startHour, startMinute):
    cursor = mysqlHandler.getCursor()
    cursor.execute("SELECT cceTeam FROM userAccounts WHERE userName='" + user + "'")
    teamName = cursor.fetchone()
    cursor.execute("SELECT userName FROM userAccounts WHERE cceTeam='" + teamName[0] + "'")
    teamMembers = cursor.fetchall()
    cursor.execute("SELECT id FROM stints")
    allIds = cursor.fetchall()
    id = allIds[len(allIds)-1][0]+1
    sql = "INSERT INTO stints (id, teamName, raceLength, stintLength, startTimeH, startTimeM, drivers) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    value = (int(id), str(teamName[0]), int(raceLength), int(stintLength), int(startHour), int(startMinute), "")
    cursor.execute(sql, value)
    mysqlHandler.getConn().commit()
