import numpy as np
import pandas as pd
import json as js
from ase.io.bader import attach_charges
from ase.visualize import view
from ase.io import read
from ase.io.bader import attach_charges
import getpass

username=getpass.getuser()

class forces:
	#define constructor
	def __init__(self):
		self.kc = 14.3996/78.4
		self.data = self.get_database("../database.js")
		#self.dataframe = self.get_dataframe( )

	def get_database(self, path_to_database):
		with open(path_to_database, "r") as file:
			data = js.load(file)
		return data

	def get_path(self, key_word):
		for key in self.data[ key_word ].keys():
			path = self.data[ key_word ][ key ]["path" ]
		path = path.replace( '~', '/home/' + username )
		return path	
			

	def get_path_for_BE(self, key_word):
		path = self.data[ key_word ][ "-1.4" ]["path"]
		path = path.replace( '~', '/home/' + username )
		return path
	
	def get_omega(self, key_word):
		path = self.get_path_for_BE( key_word )
		struc = read(path + "/OUTCAR")
		return struc.get_potential_energy()

	def get_magnitude(self, force):
		magnitude = np.sqrt( force[0]**2 + force[1]**2 + force[2]**2 )
		return magnitude

	def get_label(self, symbol):
		if symbol == "Na_top":
			return 'Na$^{+(1)}$', 'Na$^{+(2)}$'
		elif symbol == "NH4":
			return 'NH$_4^{+(1)}$', 'NH$_4^{+(2)}$'
		elif symbol == "CH3NH3":
			return '$\mathrm{CH_3NH_3^{+(1)}}$', '$\mathrm{CH_3NH_3^{+(3)}}$', '$\mathrm{CH_3NH_3^{+(3)}}$'
		elif symbol == "CH3_4N":
			return '$\mathrm{(CH_3)_4N^{+(1)}}$', '$\mathrm{(CH_3)_4N^{+(2)}}$'
		elif symbol == "NoCation":
			return 'No Explict Cation'

	#This function gets the column names of a dataframe called df
	def get_columns(self, dataframe):
		columns = list()
		for i in range(0, len(dataframe.columns)):
			columns.append(i)
		return columns
	
	def get_distance(self, key_word, C_atom, Bi_atom):
		path = self.get_path( key_word )
		struc = read(path + "/OUTCAR")
		return struc.get_distance(Bi_atom, C_atom)


	def get_angles(self, key_word, O1, C, O2):
		path = self.get_path( key_word )
		struc = read(path + "/OUTCAR")
		return struc.get_angle(O1, C, O2)

	def get_ZVAL(self, key_word):
		path = self.get_path( key_word )
		ZVAL = {}
		with open( path  + "/OUTCAR", 'r' ) as f:
			lines = f.readlines()
		for i in range( len( lines ) ):
			line = lines[ i ]
			if 'TITEL' in line:
				at = line.split()[ 3 ]
				for j in range( i, i + 10 ):
					line = lines[ j ]
					if 'ZVAL ' in line:
						zval_ = float( line.split()[ 5 ] )
						ZVAL[ at ] = zval_
		return ZVAL

	def read_file_to_dataframe(self, path_to_ACF):
		dataframe = pd.read_csv(path_to_ACF,  sep = "\s+", skiprows = 2, header = None, skipinitialspace = True, skipfooter=4, engine = "python")
		return dataframe

	
	def get_dataframe(self, key_word):
		path = self.get_path( key_word )
		struc_contcar = read(path + "/OUTCAR")
		dataframe = self.read_file_to_dataframe(path + "/ACF.dat")
		columns = self.get_columns(dataframe)
		dataframe = dataframe.drop([columns[0]], axis = 1)
		for i in range(1, 3):
			dataframe = dataframe.drop([columns[len(dataframe.columns)]], axis = 1)
		dataframe.columns = ["X", "Y", "Z", "bader_charge"]
		symbols = list()
		for i in range(0, len(dataframe)):
			symbols.append(struc_contcar.get_chemical_symbols()[i])
		dataframe["symbols"] = symbols
		
		ZVAL_dict = self.get_ZVAL( key_word )

		charge = list()
		for i in range(0, len(dataframe)):
			chg = round(ZVAL_dict[dataframe["symbols"][i]] -  dataframe["bader_charge"][i], 2)
			charge.append(chg)

		dataframe["charge"] = charge
		ZVAL = list()
		for i in range(0, len(dataframe)):
			zval = ZVAL_dict[dataframe["symbols"][i]]
			ZVAL.append(zval)

		dataframe["ZVAL"] = ZVAL
		return dataframe

	def get_total_force(self, key_word, oxygen_atoms, cation_atoms):
		dataframe = self.get_dataframe( key_word )
		forces = list()
		for i in oxygen_atoms:
			f_tot = 0
			for j in cation_atoms:
				d1 = np.array([dataframe["X"][j], dataframe["Y"][j], dataframe["Z"][j]]) - np.array([dataframe["X"][i], dataframe["Y"][i], dataframe["Z"][i]])
				d2 = d1**2
				d = d2[0] + d2[1] + d2[2]
				q = dataframe["charge"][ i ] *  dataframe["charge"][ i ]
				f = [self.kc * q/ d**(3/2)] * d1
				f_tot += f
			magnitude = self.get_magnitude(f_tot)
			forces.append( magnitude )
		return forces

	def get_plotting_dataframe(self):
		df = pd.DataFrame()
		f1 = list()
		f2 = list()
		distances = list()
		charge_CO2 = list()
		angles = list()
		systems = ["NoCation", "Na_top", "Na_side", "NH4_top", "NH4_side", "CH3NH3_top", "CH3NH3_side", "CH3NH3_reversed", "CH3_4N_top", "CH3_4N_side"]
		NoCation = [0, 0]
		
		obj = forces()
		distances.append( obj.get_distance( "bader_NoCation", 23, 96) )
		angles.append(obj.get_angles("bader_NoCation", 97, 96, 98) )
		charge_CO2.append( obj.get_dataframe("bader_NoCation")["charge"][97] + obj.get_dataframe("bader_NoCation")["charge"][96] + obj.get_dataframe("bader_NoCation")["charge"][98] )

		distances.append(obj.get_distance("bader_Na_top", 23, 96) )
		angles.append(obj.get_angles("bader_Na_top", 97, 96, 98) )
		charge_CO2.append( obj.get_dataframe( "bader_Na_top" )["charge"][97] + obj.get_dataframe("bader_Na_top")["charge"][96] + obj.get_dataframe("bader_Na_top")["charge"][98] )
		Na_top = obj.get_total_force("bader_Na_top", [97, 98], [99] )		

		distances.append( obj.get_distance("bader_Na_side", 23, 96) )
		angles.append(obj.get_angles("bader_Na_side", 97, 96, 98) )
		charge_CO2.append( obj.get_dataframe("bader_Na_side")["charge"][97] + obj.get_dataframe("bader_Na_side")["charge"][96] + obj.get_dataframe("bader_Na_side")["charge"][98] )
		Na_side = obj.get_total_force("bader_Na_side", [97, 98], [99] )
		
		distances.append(obj.get_distance("bader_NH4_top",23, 96) )
		angles.append(obj.get_angles("bader_NH4_top", 102, 96, 103) )
		charge_CO2.append( obj.get_dataframe("bader_NH4_top")["charge"][102] + obj.get_dataframe("bader_NH4_top")["charge"][96] + obj.get_dataframe("bader_NH4_top")["charge"][103] )
		NH4_top = obj.get_total_force("bader_NH4_top", [102, 103], [97, 98, 99, 100, 101] )
		
		distances.append(obj.get_distance("bader_NH4_side", 23, 96) )
		angles.append(obj.get_angles("bader_NH4_side", 102, 96, 103) )
		charge_CO2.append( obj.get_dataframe("bader_NH4_side")["charge"][102] + obj.get_dataframe("bader_NH4_side")["charge"][96] + obj.get_dataframe("bader_NH4_side")["charge"][103] )
		NH4_side = obj.get_total_force("bader_NH4_side", [102, 103], [97, 98, 99, 100, 101] )
		
		
		distances.append(obj.get_distance("bader_CH3NH3_top", 23, 97) )
		angles.append(obj.get_angles("bader_CH3NH3_top", 106, 97, 105) )
		charge_CO2.append( obj.get_dataframe("bader_CH3NH3_top")["charge"][106] + obj.get_dataframe("bader_CH3NH3_top")["charge"][97] + obj.get_dataframe("bader_CH3NH3_top")["charge"][105] )
		CH3NH3_top = obj.get_total_force("bader_CH3NH3_top", [105, 106], [96, 98, 99, 100, 101, 102, 103, 104] )

		distances.append(obj.get_distance("bader_CH3NH3_side", 23, 97) )
		angles.append(obj.get_angles("bader_CH3NH3_side", 106, 97, 105) )
		charge_CO2.append( obj.get_dataframe("bader_CH3NH3_side")["charge"][106] + obj.get_dataframe("bader_CH3NH3_side")["charge"][97] + obj.get_dataframe("bader_CH3NH3_side")["charge"][105] )
		CH3NH3_side = obj.get_total_force("bader_CH3NH3_side", [105, 106], [96, 98, 99, 100, 101, 102, 103, 104] )
		
		distances.append(obj.get_distance("bader_CH3NH3_reversed", 23, 97) )
		angles.append(obj.get_angles("bader_CH3NH3_reversed", 106, 97, 105) )
		charge_CO2.append( obj.get_dataframe("bader_CH3NH3_reversed")["charge"][106] + obj.get_dataframe("bader_CH3NH3_reversed")["charge"][97] + obj.get_dataframe("bader_CH3NH3_reversed")["charge"][105] )
		CH3NH3_reversed = obj.get_total_force("bader_CH3NH3_reversed",  [105, 106], [96, 98, 99, 100, 101, 102, 103, 104] )
		
		distances.append(obj.get_distance("bader_CH3_4N_top", 23, 99) )
		angles.append(obj.get_angles("bader_CH3_4N_top", 115, 99, 114) )
		charge_CO2.append( obj.get_dataframe("bader_CH3_4N_top")["charge"][115] + obj.get_dataframe("bader_CH3_4N_top")["charge"][99] + obj.get_dataframe("bader_CH3_4N_top")["charge"][114] )
		CH3_4N_top = obj.get_total_force("bader_CH3_4N_top", [114, 115], [96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113] )

		distances.append(obj.get_distance("bader_CH3_4N_side", 23, 99) )
		angles.append(obj.get_angles("bader_CH3_4N_side", 115, 99, 114) )
		charge_CO2.append( obj.get_dataframe("bader_CH3_4N_side")["charge"][115] + obj.get_dataframe("bader_CH3_4N_side")["charge"][99] + obj.get_dataframe("bader_CH3_4N_side")["charge"][114] )
		CH3_4N_side = obj.get_total_force("bader_CH3_4N_side", [114, 115], [96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113] )
		
		omega = list() #CO2 chem no cation
		omega.append(self.get_omega("CO2 chem no cation") -self.get_omega("clean Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("Na_top") -self.get_omega("Na/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("Na_side") -self.get_omega("Na/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("NH4_top") -self.get_omega("NH4/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("NH4_side") -self.get_omega("NH4/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("CO2 CH3NH3 top chem") -self.get_omega("CH3NH3/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("CO2 CH3NH3 side chem") -self.get_omega("CH3NH3/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("CO2 CH3NH3 reversed chem") -self.get_omega("CH3NH3/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("CH3_4N top chem") -self.get_omega("CH3_4N/Bi(111)") - self.get_omega("CO2"))
		omega.append(self.get_omega("CH3_4N side chem") -self.get_omega("CH3_4N/Bi(111)") - self.get_omega("CO2"))

		df["systems"] = systems
		for i in [NoCation, Na_top, Na_side, NH4_top, NH4_side,CH3NH3_top, CH3NH3_side, CH3NH3_reversed, CH3_4N_top, CH3_4N_side]:
			f1.append( i[0] )
			f2.append( i[1] )
		df["Fion-O1"] = f1
		df["Fion-O2"] = f2
		df["dBi_C"] = distances
		df["qCO2"] = charge_CO2
		df["OCO"] = angles
		df["Omega"] = omega
		print(df)

obj = forces()
obj.get_plotting_dataframe()
