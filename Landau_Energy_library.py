import os
import re
import math
import pandas as pd
import numpy as np
from ase.io import read

class Landau_Energy:

	def __init__( self, pH_down, pH_up ):
		self.T = 300
		self.kB = 8.617333262 * 10**(-5)
		self.ln10KT = self.T * self.kB * math.log(10)
		self.pH_down = pH_down
		self.pH_up = pH_up
		self.loc = os.getcwd()
		self.energy_H2 = self.get_omega_H2()
		self.Vol_dir =  self.get_Vol_dir()
		self.SHE_voltages = self.get_SHE_voltages()
		self.coverage_dir = self.get_coverage_dir()
		self.number_of_H = self.get_number_of_H()
		self.mu_H = self.get_mu_H()
		self.grand_canonical_energy = self.get_grand_canonical_energy()
		self.area = self.get_unit_cell_area()
		self.keys_to_drop = self.get_keys_to_drop()
		self.dictionary = self.get_Landau_energy()

	def get_Vol_dir( self ):
		voltage_dirs =  [ i for i in os.listdir( self.loc ) if ( os.path.isdir( self.loc + "/" + i ) and i.startswith( "chg" ) ) ] 
		return sorted( voltage_dirs, key= lambda x: float(x[  4 : ] ), reverse = True )

	def get_SHE_voltages( self ):
		pattern = r'-?\d+(\.\d+)?'
		return sorted( [ float(re.search(pattern, item).group()) for item in self.Vol_dir ], reverse = True )

	def get_coverage_dir( self ):
		coverages = [i for i in os.listdir(self.loc + "/" + self.Vol_dir[0]) if (i.startswith("0") or i.startswith("1ML") or i.startswith("1.")  or i.startswith("2") )]
		return sorted( coverages, key= lambda x: float(x[ : -2 ] ) )

	def get_omega_H2( self ):
		os.chdir( self.loc + "/H2")
		word = "GC Correction"
		struc = read( "OUTCAR" )
		with open( "OUTCAR", "r" )  as file:
			for line_number, line in enumerate( file ):
				if word in line:
					a = line
		correction = re.findall( r'[-+]?\d*\.\d+|\d+', a )
		correction = float(".".join( correction ) )
		return struc.get_potential_energy() - correction

	def get_number_of_H( self ):
		number_of_H = dict()
		for i in self.coverage_dir:
			os.chdir( self.loc +  "/" + self.Vol_dir[ 0 ] + "/" + i + "/target_potential")
			struc = read( "CONTCAR" )
			n = 0
			for j in struc:
				if j.symbol == "H":
					n += 1
			number_of_H[ i ] = n
		return number_of_H

	def get_unit_cell_area( self ):
		os.chdir( self.loc +  "/" + self.Vol_dir[ 0 ] + "/" + self.coverage_dir[ 0 ] +  "/target_potential/" )
		struc = read( "CONTCAR" )
		area_vec = np.cross( struc.cell[0], struc.cell[1] )
		area = np.sqrt( area_vec[ 0 ]**2 + area_vec[ 1 ]**2 + area_vec[ 2 ]**2 )
		return area

	
	def get_mu_H( self ):
		mu_H = {}
		for pH in range( self.pH_down, self.pH_up + 1 ):
			for SHE in self.SHE_voltages:
				mu_H[ str( pH ) + "_" + str( SHE )  ] =  0.5 * self.energy_H2 - self.ln10KT * pH - float( SHE )
		return mu_H

	def get_grand_canonical_energy( self ):
		grand_canonical_energy = {}
		for i in self.Vol_dir:
			for j in self.coverage_dir:
				os.chdir( self.loc + "/" + i + "/" + j + "/target_potential")
				print( "Reading file:  ", i + "_" + j + "/OUTCAR")
				struc = read("OUTCAR")
				grand_canonical_energy[ i + "_" + j ] = struc.get_potential_energy()
		return grand_canonical_energy

	def get_keys_to_drop( self ):
		keys_to_drop = list()
		for pH in range( self.pH_down, self.pH_up + 1 ):
			for SHE in self.SHE_voltages:
				keys_to_drop.append( str( pH ) + "_" + str( SHE ) + "_" + "0ML" )
		return keys_to_drop
		
	def get_Landau_energy( self ):
		keys_to_drop = list()
		Landau_energy = {}
		for SHE in self.SHE_voltages:
			for coverage in self.coverage_dir:     
				for pH in range( self.pH_down, self.pH_up + 1 ):
					Landau_energy[ str( pH ) + "_" + str( SHE ) + "_" + str( coverage ) ] = self.grand_canonical_energy[ "chg_" + str( SHE ) + "_" + str(coverage) ] - self.grand_canonical_energy[ "chg_" + str( SHE ) + "_0ML"  ] - self.number_of_H[ str( coverage ) ] * self.mu_H[ str( pH ) + "_" + str( SHE )  ]        
		Landau_energy_drop = { key: value for key, value in Landau_energy.items() if key not in self.keys_to_drop }
		Landau_energy_per_area = {key: value / self.area  for key, value in Landau_energy_drop.items()}
		return Landau_energy_per_area 
	
	def get_Landau_energy_for_pH_7( self ):
		Landau_energy = {}
		for SHE in self.SHE_voltages:
			for coverage in self.coverage_dir:     
				for pH in [ 7 ]:                 
					Landau_energy[ str( pH ) + "_" + str( SHE ) + "_" + str( coverage ) ] = self.grand_canonical_energy[ "chg_" + str( SHE ) + "_" + str(coverage) ] - self.grand_canonical_energy[ "chg_" + str( SHE ) + "_0ML"  ] - self.number_of_H[ str( coverage ) ] * self.mu_H[ str( pH ) + "_" + str( SHE )  ]        
		Landau_energy_drop = { key: value for key, value in Landau_energy.items() if key not in self.keys_to_drop }
		Landau_energy_per_area = {key: value / self.area  for key, value in Landau_energy_drop.items()}
		Landau_energy_pH_7 = {}
		for key, value in Landau_energy_per_area.items():
			coverage = key.split('_')[-1].replace( "ML", "" )
			if coverage not in Landau_energy_pH_7:
				Landau_energy_pH_7[ coverage ] = list()
			Landau_energy_pH_7[ coverage ].append( value )
		return Landau_energy_pH_7 
	
	def get_BE_per_H( self, voltage ):
		binding_energy = {}
		for SHE in self.SHE_voltages:
			for coverage in self.coverage_dir:     
				for pH in range( self.pH_down, self.pH_up + 1 ):
					binding_energy[ str( pH ) + "_" + str( SHE ) + "_" + str( coverage ) ] = self.grand_canonical_energy[ "chg_" + str( SHE ) + "_" + str(coverage) ] - self.grand_canonical_energy[ "chg_" + str( SHE ) + "_0ML"  ]
					#key = str( pH ) + "_" + str( SHE ) + "_" + str( coverage ) + " "
					#print(key,  binding_energy[ str( pH ) + "_" + str( SHE ) + "_" + str( coverage ) ])
		binding_energy_drop = { key: value for key, value in binding_energy.items() if key not in self.keys_to_drop }
		binding_energy_V_0 = {}
		dropping_keys = list()
		for key in binding_energy_drop.keys():
			if key.split("_")[ 1 ] !=  str( voltage ):
				dropping_keys.append( key )
		binding_energy_dropped = { key: value for key, value in binding_energy_drop.items() if key not in dropping_keys }
		for key, value in binding_energy_dropped.items():
			coverage = key.split('_')[ -1 ] 
			if coverage not in binding_energy_V_0:
				binding_energy_V_0[ coverage ] = list()
			binding_energy_V_0[ coverage ].append( value )
		for key in binding_energy_V_0.keys():
			binding_energy_V_0[ key ] = [ value / self.number_of_H[ key ] for value in binding_energy_V_0[ key ] ] 
		binding_energy_V_0_f = {}
		for key, value_list in binding_energy_V_0.items():
			subtracted_values = [ value - 0.5 * self.energy_H2 for value in value_list ]
			binding_energy_V_0_f[ key ] = subtracted_values
		for key, value in binding_energy_V_0_f.items():
			print( key, value )
		return binding_energy_V_0_f


	
	#for all the voltages
	def get_BE_per_H_2( self ):
		binding_energy_all_voltages = {}
		binding_energy = {}
		binding_energy_all_voltages_f = {}
		keys_to_drop = list()
		for SHE in self.SHE_voltages:
			for coverage in self.coverage_dir:     
				binding_energy[ str( SHE ) + "_" + str( coverage ) ] = self.grand_canonical_energy[ "chg_" + str( SHE ) + "_" + str(coverage) ] - self.grand_canonical_energy[ "chg_" + str( SHE ) + "_0ML"  ]
				#key = str( SHE ) + "_" + str( coverage ) + " "
				#print(key,  binding_energy[ key ] )
		for key, value in binding_energy.items():
			print( key, value )
		for SHE in self.SHE_voltages:
			keys_to_drop.append( str( SHE ) + "_" + "0ML" )
		binding_energy = { key: value for key, value in binding_energy.items() if key not in keys_to_drop }
		for key, value in binding_energy.items():
			coverage = key.split('_')[ -1 ] 
			if coverage not in binding_energy_all_voltages:
				binding_energy_all_voltages[ coverage ] = list()
			binding_energy_all_voltages[ coverage ].append( value )
		for key in binding_energy_all_voltages.keys():
			binding_energy_all_voltages[ key ] = [ value / self.number_of_H[ key ] for value in binding_energy_all_voltages[ key ] ] 
		for key, value_list in binding_energy_all_voltages.items():
			subtracted_values = [ value - 0.5 * self.energy_H2 for value in value_list ]
			binding_energy_all_voltages_f[ key ] = subtracted_values
		for key, value in binding_energy_all_voltages_f.items():
			print( key, value )
		return binding_energy_all_voltages_f





	def get_min_Landau_Energy( self, voltage, pH ):
		min_val = math.inf    
		dictionary = self.dictionary
		for coverage in self.coverage_dir[1: ]:
			current_key = str( pH ) + "_" + str( voltage ) + "_" + str( coverage )
			#print( current_key, dictionary[ current_key ] )
			if dictionary[ current_key ] < min_val:
				min_val = dictionary[ current_key ]
				key = current_key
		#print("The system with the lowest energy is:", key, "and Landau energy per H =", round( min_val, 4 ) )
		return key, min_val

	def get_data_as_DataFrame( self, pH ):
		data = {}
		df = pd.DataFrame()
		Landau_Energy = list()
		keys = list()
		dictionary = self.dictionary
		df[ "V" ] = df[ "pH" ] = df[ "Coverage" ] = df[ "Landau_Energy" ] = np.nan
		V = self.SHE_voltages
		pH_list = [ str( pH ) for i in range( 0, len( V ) ) ]
		df["pH"] = pH_list
		df["V"] = V
		for i in V:
			key, Landau_Energy_sys = self.get_min_Landau_Energy( i , pH )	
			Landau_Energy.append( Landau_Energy_sys )
			key = key.split( "_" )[ 2 : ]
			key = "_".join( key )
			keys.append( key )
		keys =  keys
		df["Coverage"] = keys
		df["Landau_Energy"] = Landau_Energy
		#print( df )
		return df

	def get_all_data_in_dictionary( self ):
		data = {}
		all_dfs = []	
		for pH in range( 0, self.pH_up + 1 ):
			df = self.get_data_as_DataFrame( pH = pH )
			data[ "pH=" + str(pH) ] = df
		for key, value in data.items():
			print( key )
			print( value )
		return data
		

class fix_data():
	
	def __init__( self , down_pH, up_pH ):
		self.down_pH = down_pH
		self.up_pH = up_pH
		self.obj = Landau_Energy( self.down_pH, self.up_pH )	
		self.dict = self.obj.get_all_data_in_dictionary()
	

	def get_pH( self ):
		pH = list()
		for i in self.dict.keys():
			pH_number = re.findall(r'\d+', i)[0]
			pH.append( int( pH_number) )		
		pH = np.arange( min(pH), max(pH) + 1 )
		print( pH )
		return pH

	def get_voltages( self ):
		voltage = list()
		key = list( self.dict.keys() )[0]  
		for i in self.dict[ key ]["V"]:
			voltage.append(  float( i )  )
		print( voltage )
		return voltage
	
	def get_plotting_data( self ):
		data = {}
		pH = list()
		V = self.get_voltages()
		voltages = list()
		Landau_Energy = list()
		coverage = list() #
		for i in range(0, ( self.up_pH + 1) * len(V)):
			pH.append( i // len( V ) )
		voltages = [ i for j in range(0, self.up_pH + 1 ) for i in V ]
		df = self.obj.get_all_data_in_dictionary()
		for i in df.keys():
			for j in range(0, len( df[ "pH=0" ][ "Landau_Energy" ] ) ):
				Landau_Energy.append( df[ i ][ "Landau_Energy" ][ j ] )
		for i in df.keys():
			for j in range(0, len( df[ "pH=0" ][ "Coverage" ] ) ):
				coverage.append( df[ i ][ "Coverage" ][ j ] )

		data[ "pH" ] =  pH 
		data[ "V" ] = voltages
		data[ "Landau_Energy" ] = Landau_Energy
		data[ "Coverage" ] = coverage	

		data_df = pd.DataFrame( data )
		pH = np.array(data_df['pH']).reshape( self.up_pH + 1,  len( V ) )
		Landau_Energy = np.array(data_df['Landau_Energy']).reshape( self.up_pH + 1,  len( V ) )
		cov = np.array(data_df['Coverage']).reshape( self.up_pH + 1,  len( V ) )
		V = np.array(data_df['V']).reshape( self.up_pH + 1,  len( V ) )
		cov = np.array([[float(value.replace('ML', '')) for value in row] for row in cov])
		return pH, V, Landau_Energy, cov

if __name__ == "__main__":
	obj = Landau_Energy( pH_down = 0, pH_up = 7 )
	a =  obj.get_all_data_in_dictionary()
	#a = obj.get_all_data_in_dictionary()
	#b = obj.get_Landau_energy_for_pH_7()
