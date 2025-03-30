import sqlite3
from PraiseBotServer.text_formatting import getNameFromUserId
import os

DB_FILE = "Praise_Database.db"

def fetch_and_update_database(usersArray, client):
    cnx = sqlite3.connect(DB_FILE)

    cursor = cnx.cursor()

    userPoints = {}


    for userId in usersArray:
        query = "SELECT points FROM users WHERE id = ?;"
        values = (userId,)
        cursor.execute(query, values)

        cursorFetch = cursor.fetchone()
        points = 1
        if cursorFetch == None: #user is not in database
            addQuery = "INSERT INTO users (id, name, points) VALUES (?, ?, ?);"
            values = (userId, getNameFromUserId(userId, client), 0)
            cursor.execute(addQuery, values)
            cnx.commit()
            print("user added to database")
        else:
            points = cursorFetch[0] + 1

        updateQuery = "UPDATE users SET points = ? WHERE id = ?;"
        updateValues = (points, userId)
        cursor.execute(updateQuery, updateValues)
        cnx.commit()

        userPoints[userId] = points

    cursor.close()
    cnx.close()

    return userPoints
