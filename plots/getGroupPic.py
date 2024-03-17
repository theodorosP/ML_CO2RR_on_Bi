import os 
import json as js
import getpass
from ase.io import read
from grouped_figures import plot_figure 
username=getpass.getuser()
import numpy as np 	

order = {} 
order2 = {}
let = ord( 'a' )   

order[ 'a' ] = {'name':'Na', 'img':'Na.png', 'energy' : " "  }   
order[ 'b' ] = {'name':'NH4', 'img':'NH4.png', 'energy' : " "  }
order[ 'c' ] = {'name':'CH3NH3', 'img':'CH3NH3.png', 'energy' : " "  }
order[ 'd' ] = {'name':'CH3_4N', 'img':'CH3_4N.png', 'energy' : " "  }


ncols = 2
nrows = 2
width  = 2 * ncols
height = 2 * nrows
output = 'pic_xdir.png'
plot_figure( order, ncols = ncols, nrows = nrows, width = width, height = height, boxcolor = 'white', textcolor='k', output = output )
output = 'pic_ydir.png'
plot_figure( order2, ncols = ncols, nrows = nrows, width = width, height = height, boxcolor = 'white', textcolor='k', output = output )

#plot_figure( order2, ncols = ncols, nrows = nrows, width = width, height = height, boxcolor = 'white', textcolor='k', output = 'angle2' + output )
