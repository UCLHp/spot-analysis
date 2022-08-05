import pypyodbc
import pandas as pd

from datetime import datetime
from datetime import timedelta

import constants as cs

DATABASE_DIR = cs.DATABASE_DIR
DB_PWD = cs.PWD


# PWD = "Pr0ton5%"

def connect_db(DATABASE_DIR,  PWD = DB_PWD):
    ''' connect to the database
    '''
    conn = None
    try:
        connection = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;PWD=%s'%(DATABASE_DIR,PWD)
    #   connection = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;PWD=%s'%(DATABASE_DIR,PWD)
        conn = pypyodbc.connect(connection)
        cursor =  conn.cursor()
        # print(f'connection : {connection}')
        # print(f'conn: {conn}')
        # print(f'cursor: {cursor}')
    except:
        return False, False
        print(f'>> cannot connect with the database. Bye~')

    return conn, cursor

def get_mea_time(spotpatterns):
    ''' spotpatterns is a dictionary containing five objects from five energies.
    DATABASE_DIR is a string of directory to the ASSESS database
    table_name is a string, the table name in the ASSESS database
    '''
    # current = datetime.now()

    times = []
    for en in spotpatterns.keys():
        times.append(spotpatterns[en].output.datetime)

    return max(times)

def push_session_data(DATABASE_DIR, session_data,  PWD = DB_PWD ):
    ''' DATABASE_DIR >> path_to_.accdb
        session_data >> a list [AData, MachineName,  Device, ganry angle, Operator1, Operator2, Comments]'''

    conn, cursor = connect_db(DATABASE_DIR , PWD = DB_PWD)

    # sql = '''
    #       INSERT INTO SpotPositionSession VALUES (?, ?, ?, ?, ?, ?, ?)
    #
    #       '''
    #
    sql = '''
          INSERT INTO SpotPositionSession VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          '''

    # try:
    cursor.execute(sql, session_data)
    conn.commit()
    return True
# except:
    print(f' >> fail to push session result to session table in the ASSESS database')
    return False

    return

def push_spot_data(DATABASE_DIR, spot_results, PWD = DB_PWD ):
    ''' DATABASE_DIR >> path_to_.accdb
        spot_results >> a nested list. for each list: [date, gantry, energy, device, gantry angle,
        spot_location name, x-pos (measured), y-pos (measured),
        horprof.rgrad, horprof.lgrad, horprof.fwhm,
        vertprof.rgrad, vertprof.lgrad, vertprof.fwhm,
        bltr.rgrad, bltr.lgrad, bltr.fwhm,
        tlbr.rgrad, tlbr.lgrad, tlbr.fwhm,
        ]
        '''

    conn, cursor = connect_db(DATABASE_DIR, PWD = DB_PWD)

    sql = '''
          INSERT INTO SpotPositionResults VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

          '''


    try:
        for i, val in enumerate(spot_results):
            cursor.execute(sql, val)
            conn.commit()

            if i == 0:
                print(f'>> All {val[2]}MeV spot results measured at gantry angle {val[4]} are pushed to database! ')

        return True
    except:
        print(f' >> fail to push spot results to spot data table in the ASSESS database')
        return False

    return

def fetch_db(DATABASE_DIR, table, col,  *, PWD = DB_PWD):
    ''' A function to pull out a column from  a table in the db
        DATABASE_DIR = database location
        table = name of the table
        column = name of the column'''

    conn, cursor = connect_db(DATABASE_DIR , PWD = DB_PWD)

    if conn == False:
        col_lt = False
    else:
        col = cursor.execute(f'SELECT {col} FROM [{table}]')
        col = col.fetchall()
        col_lt = []
        for i in col:
            col_lt.append(list(i)[0])

    return col_lt
