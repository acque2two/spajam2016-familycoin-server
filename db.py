import os
import subprocess


def createDb(dbName):
    if int(os.environ.get("PORT", 111111)) != 111111:
        subprocess.Popen("sqlite3 " + dbName + " < dbTable.sql", shell=True)
    pass

# createDb(sqlite3.connect("a"))
