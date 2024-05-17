from  libdatabase import *
import os

loc = os.getcwd() + "/"
with open( loc + 'database_theo.js', 'r' ) as f:
    database = js.load( f )

test_database( database, Vthreshold = 0.005, log = 'theo_verify.log' )
