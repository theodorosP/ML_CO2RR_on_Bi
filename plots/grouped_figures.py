# plot_pdos.py  
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from ase.io import read
from dlePy.vasp.doscar import get_pdos, parse_info, gen_doscars
import gzip as gz
import matplotlib.image as mpimg


def convert_path( path_in ):
    return path_in.replace( '~', '/home/' + username )

def show_im( ax, img, label, ener, textcolor = 'white', name = "", alpha = 1.0 ):
    xmax = img.shape[ 0 ]
    ymax = img.shape[ 1 ]
    ymin = 0
    xmin = 0 
    ax.imshow( img, alpha = alpha )
    #ax.axis( 'off' )
    ax.set_xticks( [] )
    ax.set_yticks( [] )
    #ax.text( -xmax* 0., ymax* 0.85,  '(' + str(label) + ')', color = textcolor, fontsize = 16, fontweight = 'bold', va = 'top', ha = 'left', bbox=dict(facecolor='white', edgecolor='none', alpha = 0.5, pad=1.0) )
    #ax.text( xmax * 0.98, ymin + (ymax-ymin) * 0.02, name, color = textcolor, fontsize = 10, va = 'top', ha = 'right', bbox=dict(facecolor='white', edgecolor='none', alpha = 0.5, pad=1.0) )
    #ax.text( xmax * 0.98, ymin + (ymax-ymin) * 0.98, r'charge = ' +  str(ener) , color = textcolor, fontsize = 10, va = 'bottom', ha = 'right', bbox=dict(facecolor='white', edgecolor='none', alpha = 0.5, pad=1.0) )

def plot_figure( images, ncols = 1, nrows = 1, width = 2, height = 2, boxcolor = 'white', textcolor = 'white', output = 'output.png' ):
    fig = plt.figure( figsize = ( width, height ) )
    matplotlib.rc('axes',edgecolor=boxcolor, linewidth = 2 )
    for i, key in enumerate( sorted( images.keys()) ):
        ax  = fig.add_subplot( nrows, ncols, i + 1  ) 
        print( images[ key ][ 'img' ] ) 
        im = mpimg.imread( images[ key ][ 'img'] )
        name = images[ key ][ 'name']
        ener = images[ key ][ 'energy'] 
        print( name,key ) 
        show_im( ax, im, key, ener, textcolor = textcolor, name = name, alpha = 1.0 )
    plt.subplots_adjust(left=0.05, right=1., top=1., bottom=0.0, wspace=0.1, hspace= 0.00)
    plt.savefig( output, dpi = 600 )

if __name__ == "__main__":
    import getpass
    from ase.io import read
    import json as js

    image_folder = '/storage/data2/PROJ/SAC/duy/PUBLICATIONS/Figures/'
    username=getpass.getuser()
    with open( '/storage/data2/PROJ/SAC/duy/PUBLICATIONS/database.js', 'r' ) as f:
        data = js.load( f )
    keys = [ x for x in data.keys() ]

    for i, item in enumerate( sorted( keys ) ):
        if '110_small' in item and 'PtCevDis/' in item:
            print ( item, 1, len( keys )  )


    NH3 = read( data[ 'NH3' ][ 'path' ] + '/OUTCAR' )
    images = {}
    # Get NH3@
    item = 'PtCevDis/110_small'
    loc  = convert_path( data[ item ][ 'path' ] )
    sub  = read( loc + '/OUTCAR' )
    images[ 0 ] = { 'name' : item.replace( '/110_small','').replace( 'NH3','NH$_3$'),
                     'img' : image_folder + item.replace( '/','_') + '.png',
                  'energy' : 0 }

    NH3_items = [ x for x in data.keys() if 'NH3' in x and 'PtCevDis/110_small' in x]
    NH3_items  = [ 'NH3@leftCe/PtCevDis/110_small', 'NH3@Pt/PtCevDis/110_small', 'NH3@Pt_2/PtCevDis/110_small', 'NH3@O/PtCevDis/110_small', 'NH3@Ce/PtCevDis/110_small' ]


    print ( NH3_items )
    istart = 1
    for i, item in enumerate( NH3_items ):
        loc = convert_path( data[ item ][ 'path' ] )
        system = read( loc + '/OUTCAR' )
        ener = system.get_potential_energy()
        images[ i + istart ] = { 'name' : item.replace( '/110_small','').replace( 'NH3','NH$_3$'), 
                                  'img' : image_folder + item.replace( '/','_') + '.png', 
                               'energy' : ener - NH3.get_potential_energy() - sub.get_potential_energy() }
    istart = i + istart + 1

    item = 'PtCeOv/110_small'
    loc  = convert_path( data[ item ][ 'path' ] )
    sub  = read( loc + '/OUTCAR' )
    images[ istart ] = { 'name' : item.replace( '/110_small','').replace( 'NH3','NH$_3$'),
                     'img' : image_folder + item.replace( '/','_') + '.png',
                  'energy' : 0 }

    NH3_items = [ x for x in data.keys() if 'NH3' in x and 'PtCeOv/110_small' in x]
    NH3_items = ['NH3@Ce4/PtCeOv/110_small', 'NH3@O/PtCeOv/110_small', 'NH3@Ce/PtCeOv/110_small']
    #NH3_items  = [ 'NH3@leftCe/PtCevDis/110_small', 'NH3@Pt/PtCevDis/110_small', 'NH3@Pt_2/PtCevDis/110_small', 'NH3@O/PtCevDis/110_small', 'NH3@Ce/PtCevDis/110_small' ]
    for i, item in enumerate( NH3_items ):
        loc = convert_path( data[ item ][ 'path' ] )
        system = read( loc + '/OUTCAR' )
        ener = system.get_potential_energy()
        images[ i + istart + 1 ] = { 'name' : item.replace( '/110_small','').replace( 'NH3','NH$_3$'),
                                  'img' : image_folder + item.replace( '/','_') + '.png',
                               'energy' : ener - NH3.get_potential_energy() - sub.get_potential_energy() }
 
    ncols = 6
    nrows = 2
    width  = 12 
    height = 4
    output = 'NH3_Adsorption.png'
    plot_figure( images, ncols = ncols, nrows = nrows, width = width, height = height, boxcolor = 'white', textcolor='k', output = output )

