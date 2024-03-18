import os
import re
import json as js
from ase.io import read
import pandas as pd
import matplotlib.pyplot as plt

import getpass

username=getpass.getuser()

class plotting():
	#define constructor
	def __init__(self):
		self.legend_font = 8
		self.labelpadx = 0.5
		self.labelpady = 0.5
		self.tick_font = 10
		self.axis_font = 12
		self.plt_h = 2.5
		self.plt_w = 3.5
		self.dpi = 600
		self.m_left = 0.18
		self.m_right = 0.98
		self.m_bottom = 0.17
		self.m_top = 0.99
		self.data = self.get_database("../database.js")

	def get_database(self, path):
		with open(path, "r") as file:
			data = js.load(file)
		return data
	
	def get_omega(self, path):
		struc = read(path + "/OUTCAR")
		return struc.get_potential_energy()

	
	def get_energy_CO2_box_correction(self):
		word = "GC Correction"
		for key in self.data[ "CO2" ].keys():
			path = self.data[ "CO2" ][ key ]["path" ]
		#path = path.replace( '~', '/home/' + username )
		#struc = read(path + "/OUTCAR")
		#with open( path +  "/OUTCAR", "r" )  as file:
		#	for line_number, line in enumerate(file):
		#		if word in line:
		#			a = line
		#correction = re.findall(r'[-+]?\d*\.\d+|\d+', a)
		#correction = float(".".join(correction))
		struc = read(path + "/OUTCAR")
		return struc.get_potential_energy()
		#return struc.get_potential_energy() - correction 
	
	def get_V_and_omega(self, key_word, data):
		V = list()
		omega = list()
		for key in data[ key_word ].keys():
			V.append( float(key) )
			path = data[ key_word ][ key ]["path" ]
			omega.append( self.get_omega( path ) )
		return V, omega
		
	def get_delta_omega(self, key_word_with_CO2, key_word_without_CO2):
		V_CO2, Omega_CO2 = self.get_V_and_omega(key_word_with_CO2, self.data)
		V_without_CO2, Omega_without_CO2 = self.get_V_and_omega(key_word_without_CO2, self.data)
		index = V_without_CO2.index( V_CO2[0] )
		V_without_CO2 = V_without_CO2[ index: ]
		Omega_without_CO2 = Omega_without_CO2[ index: ]
		CO2_delta_omega = [w1 - w2 - self.get_energy_CO2_box_correction() for w1, w2 in zip( Omega_CO2, Omega_without_CO2 )]
		return CO2_delta_omega, V_CO2

	def plot_BE_vs_V(self, name):
		delta_omega_NoCation = self.get_delta_omega("CO2 chem no cation", "clean Bi(111)")[0]
		V_NoCation = self.get_delta_omega("CO2 chem no cation", "clean Bi(111)")[1]
		delta_omega_Na = self.get_delta_omega("CO2 Na side chem", "Na/Bi(111)")[0]
		V_Na = self.get_delta_omega("CO2 Na side chem", "Na/Bi(111)")[1]
		delta_omega_NH4 = self.get_delta_omega("CO2 NH4 top chem", "NH4/Bi(111)")[0]
		V_NH4 = self.get_delta_omega("CO2 NH4 top chem", "NH4/Bi(111)")[1]
		delta_omega_CH3NH3 = self.get_delta_omega("CO2 CH3NH3 reversed chem", "CH3NH3/Bi(111)")[0]
		V_CH3NH3 = self.get_delta_omega("CO2 CH3NH3 reversed chem", "CH3NH3/Bi(111)")[1]
		delta_omega_CH3_4N = self.get_delta_omega("CH3_4N side chem", "CH3_4N/Bi(111)")[0]
		V_CH3_4N = self.get_delta_omega("CH3_4N side chem", "CH3_4N/Bi(111)")[1]
		
		fig = plt.figure(figsize=(self.plt_w, self.plt_h))
		ax = fig.add_subplot(1, 1, 1 )
		x_max = -0.7
		x_min = -2.1
		y_max = 0.5
		y_min = -0.8
		x_ticks = [-2.0, -1.8, -1.6, -1.4, -1.2, -1.0, -0.8]
		y_ticks = [-0.5, 0, 0.5]
		Lx = x_max - x_min
		Ly = y_max - y_min
		ax.set_ylim( y_min, y_max )
		ax.set_xlim( x_min, x_max )		
		ax.plot( V_NoCation, delta_omega_NoCation, 'o-', linewidth=1, markersize=4, label = "No  Explicit Cation" )
		ax.plot( V_Na, delta_omega_Na, '^-', linewidth=1, markersize=4, label = "Na$^{+(2)}$" )
		ax.plot(V_NH4, delta_omega_NH4, 's-', linewidth=1, markersize=4, label= "NH$_4^{+(1)}$")
		ax.plot(V_CH3NH3, delta_omega_CH3NH3, '+-', linewidth=1, markersize=4, label= "NH$_3$CH$_3^{+(3)}$")
		ax.plot(V_CH3_4N, delta_omega_CH3_4N, '*-', linewidth=1, markersize=4, label= "(CH$_3$)$_4$N$^{+(2)}$")
		yticks = y_ticks 
		ax.set_yticks( yticks )
		ax.set_yticklabels( [ str(x) for x in yticks ], fontsize = self.tick_font )
		ax.set_ylabel( '$\Delta\Omega_{ads}$ (eV)', fontsize = self.axis_font, labelpad = self.labelpady )
		xticks = x_ticks
		ax.set_xticks( xticks )
		ax.set_xticklabels( [ str( x ) for x in xticks ], fontsize = self.tick_font )
		ax.hlines( 0, x_min, x_max, lw = 0.5, color = 'gray' )
		ax.set_xlabel( '$\Phi$ (V vs RHE)', fontsize = self.axis_font, labelpad = self.labelpadx )
		ax.legend( fontsize = self.legend_font )
		plt.subplots_adjust(left=self.m_left, right = self.m_right, top = self.m_top, bottom = self.m_bottom, wspace = 0.00, hspace= 0.0 )
		plt.savefig(name, dpi = self.dpi )
		plt.show()

obj = plotting()
obj.get_delta_omega("CO2 Na top chem", "Na/Bi(111)")
obj.plot_BE_vs_V("BE_vs_V")
