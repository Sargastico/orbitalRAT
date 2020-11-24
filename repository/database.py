import sqlite3
from typing import Tuple
import resources.logcall as log
import resources.api as api
import json

connection = None

def getConnection() -> Tuple[connection, Exception]:

    global connection

    # If connection is not initialized by some reason
    if connection == None:
        connection, exception = initConnection()

    return connection, exception

def initConnection():

    global connection

    if connection == None:

        try:
            connection = sqlite3.connect('repository/satellite.db')

        except Exception as exception:

            connection = None
            return None, exception

    return connection, None

def updateDatabase(api_key):

    connection, e = getConnection()

    cursor = connection.cursor()

    cursor.execute('SELECT id FROM lastID')
    result = cursor.fetchone()
    last_id = result[0]

    logg = log.setup_logger()

    logg.info('UPDATING DATABASE')

    while True:

        last_id = int(last_id) + 1

        resp = api.rawJsonInfoRequest(last_id)
        data = json.loads(resp.text)

        if 'error' in resp.text:

            logg.error("UPDATE PROCESS FAILED: " + data['error'])
            last_id = last_id - 1
            last_id = str(last_id)
            cursor.execute("UPDATE lastID SET id = ?", (last_id,))
            connection.commit()
            raise api.ApiExceededException("API Error - exceeded the number of transactions allowed per hour")

        data = data['info']
        satname = data['satname']
        satid = data['satid']

        if(satname == "null"):

            last_id = last_id - 1
            last_id = str(last_id)
            cursor.execute("UPDATE * SET id = ?", (last_id,))
            connection.commit()

            break

        cursor.execute("INSERT INTO satellites (nome, id) VALUES (?,?)", (satname, satid))

    connection.commit()

def getSatelliteIdByUniqueName(satname):

    connection, e = getConnection()
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM satellites WHERE nome = ?', (satname,))
    result = cursor.fetchall()

    return result[0][0]