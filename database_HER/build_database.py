import json as js
import os
import getpass
import numpy as np
from ase.io import read
from dlePy.jobmon.monitor import if_vasp_done
from dlePy.vasp.getdata import get_energy
from dlePy.vasp.tpot import cal_omega, parse_outcar, get_NELECT, get_pot 

username=getpass.getuser()

keywords = [ 'path', 'note' ]
def db_add_key( database, key ):
    if key in database.keys():
        print ( "key %s already exit" %(key) )
    else:
        database[ key ] = {}

def db_add( database, key, name, input ):
    '''
    key: name of the entry
    input: A dict with few or all keywords listed in `keywords`
           'path' must be included
    '''
    if name in database[ key ].keys():
        print ( "ERROR: %s already exit in %s" %(str( name ),  key) )
        exit()
    if 'path' not in input.keys():
        print ( "ERROR: path is required %s" %(input) )
        exit()
    
    database[ key ][ name ] = input 

def db_update( database, key, name, input ):
    if 'path' not in input.keys():
        print ( "ERROR: path is required %s" %(input) )
        exit()
    if name not in database[ key ].keys():
        print ( "ERROR: %s does not exit in %s" %(str( name ),  key) )
        exit()

    if key not in database.keys():
        print ( "ERROR: %s does not exit" %( key) )
        exit()

    database[ key ][ name ] = input

def db_save( database, fout ):
    with open( fout, 'w' ) as f:
       js.dump( database, f, indent = 4 )

def db_load( database, fin ):
    with open( fin, 'r' ) as f:
       database  = js.load( f )

def convert( path ):
    return path.replace( '~', '/home/' + username )


if __name__ == "__main__":
        database = {}
        
        # For NoCation
        for i in [ "0.0", "-0.5", "-1.0", "-1.5", "-2.0", "-2.5" ]:
            loc = '~/PROJ_ElectroCat/theodoros/HER/Pt_hol/chg_' + i + "/"
            key = 'NoCation_chg_' + i 
            db_add_key( database, key )
            for name in [ x for x in os.listdir( convert( loc ) ) ]:
                #print( str( loc ) +  str( name ) + "/target_potential"  )
                # Now we need to add all path to all potentials for tihs key
                path = str( loc ) +  str( name ) + "/target_potential/"
                input = { 'path': path, 'note': "" }
                db_add( database, key, name, input )   # Add to the database


    
        for i in [ "0.0", "-0.5", "-1.0", "-1.5", "-2.0", "-2.5" ]:
            loc = "~/PROJ_ElectroCat/theodoros/HER/Pt_hol/testing/chg_" + i  + "/"  
            key = 'NoCation_testing_chg_' + i
            db_add_key( database, key )
            for name in [ x for x in os.listdir( convert( loc ) ) ]:
                #print( str( loc ) +  str( name ) + "/target_potential"  )
                # Now we need to add all path to all potentials for tihs key
                path = str( loc ) +  str( name ) + "/target_potential/"
                input = { 'path': path, 'note': "" }
                db_add( database, key, name, input )


        db_save( database, 'database_theo.js' )  #Save the database
