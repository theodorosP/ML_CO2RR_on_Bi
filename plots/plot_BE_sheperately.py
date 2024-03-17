import os
import re
import json as js
from ase.io import read
import pandas as pd
import matplotlib.pyplot as plt

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

	def get_database(self, path):
		with open(path, "r") as file:
			data = js.load(file)
		return data
	
	def get_omega(self, path):
		struc = read(path + "/OUTCAR")
		return struc.get_potential_energy()

	
	def get_energy_CO2_box_correction(self):
		word = "GC Correction"
		loc = "/home/theodoros/PROJ_ElectroCat/theodoros/energy_paths/charge/CO2_box/"
		struc = read(loc + "OUTCAR")
		with open( loc +  "/OUTCAR", "r" )  as file:
			for line_number, line in enumerate(file):
				if word in line:
					a = line
		correction = re.findall(r'[-+]?\d*\.\d+|\d+', a)
		correction = float(".".join(correction))
		return struc.get_potential_energy() - correction 
	
	def get_V_and_omega(self, key_word, data):
		V = list()
		omega = list()
		for key in data[ key_word ].keys():
			V.append( float(key) )
			path = data[ key_word ][ key ]["path" ]
			omega.append( self.get_omega( path ) )
		return V, omega
		
	def get_delta_omega(self, key_word_with_CO2, key_word_without_CO2):
		data = self.get_database("../database.js")
		V_CO2, Omega_CO2 = self.get_V_and_omega(key_word_with_CO2, data)
		V_without_CO2, Omega_without_CO2 = self.get_V_and_omega(key_word_without_CO2, data)
		index = V_without_CO2.index( V_CO2[0] )
		V_without_CO2 = V_without_CO2[ index: ]
		Omega_without_CO2 = Omega_without_CO2[ index: ]
		CO2_delta_omega = [w1 - w2 - self.get_energy_CO2_box_correction() for w1, w2 in zip( Omega_CO2, Omega_without_CO2 )]
		return CO2_delta_omega, V_CO2

	def get_label(self, symbol):
		if symbol == "Na":
			return 'Na$^{+(1)}$', 'Na$^{+(2)}$'
		elif symbol == "NH4":
			return 'NH$_4^{+(1)}$', 'NH$_4^{+(2)}$'
		elif symbol == "CH3NH3":
			return '$\mathrm{CH_3NH_3^{+(1)}}$', '$\mathrm{CH_3NH_3^{+(3)}}$', '$\mathrm{CH_3NH_3^{+(3)}}$'
		elif symbol == "CH3_4N":
			return '$\mathrm{(CH_3)_4N^{+(1)}}$', '$\mathrm{(CH_3)_4N^{+(2)}}$'
		elif symbol == "NoCation":
			return 'No Explict Cation'
			
	def plot_frame(self, counter, x_max, x_min, y_max, y_min, name,  y_ticks, x_ticks, symbol, V1, delta_omega1, V2=None, delta_omega2=None, V3=None, delta_omega3=None):
		labels = self.get_label( symbol )
		fig = plt.figure(figsize=(self.plt_w, self.plt_h))
		ax = fig.add_subplot(1, 1, 1 )
		Lx = x_max - x_min
		Ly = y_max - y_min
		ax.set_ylim( y_min, y_max )
		ax.set_xlim( x_min, x_max )		
		ax.plot( V1, delta_omega1, 'o-', linewidth=1, markersize=4, label = labels[0] )
		if V2 is not None and delta_omega2 is not None:
			ax.plot( V2, delta_omega2, 's-', linewidth=1, markersize=4, label = labels[1] )
		if V3 is not None and delta_omega3 is not None:
			ax.plot(V3, delta_omega3, '^-', linewidth=1, markersize=4, label= labels[2])
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
		ax.text( (x_max - x_min)*(-0.13)+x_min, (y_max-y_min)*0.99+y_min, '(' + counter + ')', fontweight = 'bold', fontsize = 10, va = 'top', ha = 'right' )
		plt.subplots_adjust(left=self.m_left, right = self.m_right, top = self.m_top, bottom = self.m_bottom, wspace = 0.00, hspace= 0.0 )
		plt.savefig(name, dpi = self.dpi )
		plt.show()
		
	def plot(self):
		#Na
		x_max = -0.7	
		x_min = -2.2
		y_max = 0.9
		y_min = -3
		x_ticks = [-2.0, -1.8, -1.6, -1.4, -1.2]
		y_ticks = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5]
		self.plot_frame('a', x_max, x_min, y_max, y_min, "Na", y_ticks, x_ticks, "Na", self.get_delta_omega("CO2 Na top chem", "Na/Bi(111)")[1], self.get_delta_omega("CO2 Na top chem", "Na/Bi(111)")[0], self.get_delta_omega("CO2 Na side chem", "Na/Bi(111)")[1], self.get_delta_omega("CO2 Na side chem", "Na/Bi(111)")[0])
		
		#NH4
		x_max = -0.7
		x_min = -2.2
		y_max = 1.65
		y_min = -3.5
		x_ticks = [-2.0, -1.8, -1.6, -1.4, -1.2, -1.0]
		y_ticks = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5]
		self.plot_frame('b', x_max, x_min, y_max, y_min, "NH4", y_ticks, x_ticks, "NH4", self.get_delta_omega("CO2 NH4 top chem", "NH4/Bi(111)")[1], self.get_delta_omega("CO2 NH4 top chem", "NH4/Bi(111)")[0], self.get_delta_omega("CO2 NH4 side chem", "NH4/Bi(111)")[1], self.get_delta_omega("CO2 NH4 side chem", "NH4/Bi(111)")[0])


		#CH3NH3
		x_max = -0.7
		x_min = -2.2
		y_max = 0.4
		y_min = -0.7
		x_ticks = [-2.0, -1.8, -1.6, -1.4, -1.2, -1.0, -0.8]
		y_ticks = [-0.5, -0.3, -0.1, 0.1, 0.3]
		self.plot_frame('c', x_max, x_min, y_max, y_min, "CH3NH3", y_ticks, x_ticks, "CH3NH3", self.get_delta_omega("CO2 CH3NH3 top chem", "CH3NH3/Bi(111)")[1], self.get_delta_omega("CO2 CH3NH3 top chem", "CH3NH3/Bi(111)")[0], self.get_delta_omega("CO2 CH3NH3 side chem", "CH3NH3/Bi(111)")[1], self.get_delta_omega("CO2 CH3NH3 side chem", "CH3NH3/Bi(111)")[0],  self.get_delta_omega("CO2 CH3NH3 reversed chem", "CH3NH3/Bi(111)")[1],  self.get_delta_omega("CO2 CH3NH3 reversed chem", "CH3NH3/Bi(111)")[0])
		

		#CH3_4N
		x_max = -0.7
		x_min = -2.2
		y_max = 1.65
		y_min = -3.7
		x_ticks = [-2.0, -1.8, -1.6, -1.4, -1.2, -1.0]
		y_ticks = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5]
		self.plot_frame('d', x_max, x_min, y_max, y_min, "CH3_4N", y_ticks, x_ticks, "CH3_4N", self.get_delta_omega("CH3_4N top chem", "CH3_4N/Bi(111)")[1], self.get_delta_omega("CH3_4N top chem", "CH3_4N/Bi(111)")[0], self.get_delta_omega("CH3_4N side chem", "CH3_4N/Bi(111)")[1], self.get_delta_omega("CH3_4N side chem", "CH3_4N/Bi(111)")[0] )  

obj = plotting()
obj.get_delta_omega("CO2 Na top chem", "Na/Bi(111)")
obj.plot()
