import json as js
import os
import getpass
import numpy as np
from ase.io import read
from dlePy.jobmon.monitor import if_vasp_done
from dlePy.vasp.getdata import get_energy
from dlePy.vasp.tpot import cal_omega, parse_outcar, get_NELECT, get_pot 
from tqdm import tqdm

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
    if '/home/' in path:
        username_ = path.split('/')[2]
        path = path.replace( '/home/' + username_, '/home/'+ username )
    return path.replace( '~', '/home/' + username )

def test_database( database, Vthreshold = 0.005, log = 'log' ):
    fout = open( log, 'w' )
    print_test(  fout, 'key', 'name', 'image', 'Good POT', 'JOB DONE', 'GC', 'ERROR' )
    s = '=========================================================================\n'
    fout.write( s ) 
    for key in database.keys():
        print( 'Verifying ', key )
        for name in tqdm( sorted( database[ key ].keys() ) ): 
            #if ('0ML' or "0.11ML" or "0.22ML" or "0.33ML" or "0.44ML" or "0.55ML" or "0.66ML" or "0.77ML" or "0.88ML" or "1ML" or "1.11ML" or "1.22ML" or "1.33ML" or "1.44ML" or "1.55ML" or "1.66ML" or "1.77ML" or "1.88ML" or "2ML") in name:
            #    verify( fout, database, key, name, image = None, Vthreshold = Vthreshold )
            if any(coverage in name for coverage in ["0ML", "0.11ML", "0.22ML", "0.33ML", "0.44ML", "0.55ML", "0.66ML", "0.77ML", "0.88ML", "1ML", "1.11ML", "1.22ML", "1.33ML", "1.44ML", "1.55ML", "1.66ML", "1.77ML", "1.88ML", "2ML"]):
                    verify(fout, database, key, name, image=None, Vthreshold=Vthreshold)
            if 'NEB' in name:
                loc = database[ key ][ name ][ 'path' ]
                for image in [ x for x in sorted( os.listdir( convert( loc ) ) ) if os.path.isdir( convert( loc ) + '/' + x ) ]:
                    verify( fout, database, key, name, image = image, Vthreshold = Vthreshold )
    fout.write( s ) 
    print_test(  fout, 'key', 'name', 'image', 'Good POT', 'JOB DONE', 'GC', 'ERROR' )
    fout.close()

def print_test( fout, key, name, image, good_pot, job_done, good_GC, ERROR ):
    fout.write( "%-10s %-20s %-10s %-10s %-10s %-10s %-s\n" %( key, name, image, good_pot, job_done, good_GC, ERROR ) )

def verify( fout, database, key, name, image=None, Vthreshold = 0.005 ):
    path = database[ key ][ name ][ 'path' ]
    if image != None:
        path = path + '/' + image
    good_pot = False
    job_done = False
    good_GC = False
    ERROR = 'NONE'
    print( path )
    try:
        cpot, tpot = get_pot( convert( path ) + '/OUTCAR' )
        if np.abs( cpot - tpot ) < Vthreshold:
            good_pot = True
        job_done, niter, NWS, mtime = if_vasp_done( convert( path ) + '/OUTCAR' )
        if NWS == niter:
            job_done = False
        #GC correction
        with open( convert( path ) + '/OUTCAR', 'r' ) as f:
            lines = f.readlines()
        for i in range( len( lines ) - 1, -1 , -1 ):
            if 'GC Correction         =' in lines[ i ]:
                gc_cal  = float( lines[ i ].split()[3] )
            if 'CURRENT NELECT      =' in lines[ i ]:
                NELECT = float( lines[ i ].split()[ 3 ] )
            if 'EFERMI              =' in lines[ i ]:
                EFERMI = float( lines[ i ].split()[ 2 ] )
                break
        for i in range( len( lines ) ):
            if 'number of electron   ' in lines[ i ]:
                ZVAL = float( lines[ i ].split()[ 3 ] )
                break
        gc_diff = np.abs( gc_cal + EFERMI * ( NELECT - ZVAL ) )
        if gc_diff < 0.0001:
            good_GC = True
    except:
        ERROR = '!!!NOTE!!!: ERROR WITH READING OUTCAR'
    print_test(  fout, key, name, image, good_pot, job_done, good_GC, ERROR )
