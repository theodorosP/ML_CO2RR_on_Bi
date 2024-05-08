import os
import re
import math
import numpy as np
from ase.io import read 


def get_NELECT_neutral( outcar ):
	from ase.io import read
	with open( outcar, 'r' ) as f:
		lines = f.readlines( )
	atomic = {}
	for il in range( len( lines ) ):
		line = lines[ il ]
		if 'TITEL  =' in line:
			element = line.split()[3]
		if 'ZVAL' in line and 'POMASS' in line:
			zval = float( line.split()[5] )
			atomic[ element ] = zval
	system = read( outcar )
	NELECT = 0
	for at in system:
		NELECT += atomic[ at.symbol ]
	return NELECT


#get FermiShift, CurrentPotential, Nelectcurrent, DFTenergy, FermiEnergy
def get_FS_CP_N_DFTe_FE(outcar):
	import re
	from ase.io import read
	struc = read(outcar)
	word_1 = "NELECT "
	word_2 = "FERMI_SHIFT "
	word_3 = "CURRENT POTENTIAL"
	word_4 = "EFERMI"
	energy = struc.get_potential_energy()
	with open("OUTCAR", "r") as file:
		for line_number, line in enumerate(file):
			if word_1 in line:
				NELECT = line
			if word_2 in line:
				fermi_shift = line
			if word_3 in line:
				current_potential = line
			if word_4 in line:
				fermi_energy = line
	fermi_energy = re.findall(r'(-?\d+)', fermi_energy)
	fermi_energy = float(".".join(fermi_energy))	
	NELECT = re.findall(r'\d+', NELECT)
	NELECT = float(".".join(NELECT))
	current_potential = re.findall(r'(-?\d+)', current_potential)
	current_potential = float(".".join(current_potential))
	fermi_shift = re.findall(r'(-?\d+)', fermi_shift)
	fermi_shift = float(".".join(fermi_shift))
	return  -fermi_shift, current_potential, NELECT, energy, fermi_energy



def calc_omega(outcar):
	data = get_FS_CP_N_DFTe_FE(outcar)
	NELECT = get_NELECT_neutral(outcar)
	q = NELECT - data[ 2 ]
	phi_vac = data[ 0 ]
	phi = data[ 1 ]
	omega = data[ 3 ] + q * (phi_vac - phi) #data[4]
	return omega




class Grand_Free_Energy:

	def __init__( self, path_to_the_full_system, path_to_the_clean_substrate, path_to_H2, pH ):
		self.pH = pH
		self.T = 300
		self.kB = 8.617333262 * 10**(-5)
		self.ln10KT = self.T * self.kB * math.log(10)
		self.path_to_the_full_system = path_to_the_full_system
		self.path_to_the_clean_substrate = path_to_the_clean_substrate
		self.path_to_H2 = path_to_H2
		self.energy_H2 = self.get_omega_H2()
		self.number_of_H = self.get_number_of_H()
		self.area = self.get_unit_cell_area()	
		self.SHE = self.get_SHE_voltage()

	def get_omega_H2( self ):
		os.chdir( self.path_to_H2 )
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
		os.chdir( self.path_to_the_full_system )
		struc = read( "CONTCAR" )
		n = 0
		for j in struc:
			if j.symbol == "H":
				n += 1
		return n 

	def get_unit_cell_area( self ):
		os.chdir( self.path_to_the_full_system  )
		struc = read( "CONTCAR" )
		area_vec = np.cross( struc.cell[0], struc.cell[1] )
		area = np.sqrt( area_vec[ 0 ]**2 + area_vec[ 1 ]**2 + area_vec[ 2 ]**2 )
		return area

	def get_SHE_voltage( self ):
		os.chdir( self.path_to_the_full_system )
		key_word = "CURRENT POTENTIAL   =" 
		with open( "OUTCAR", "r" ) as file:
			lines = file.readlines()
		for line in reversed( lines ):
			if key_word in line:
				result = re.findall(r'\d+\.\d+|\d+', line )
				result = round( float( "".join( result ) ), 2 )
				return result - 4.43
				break

	def get_grand_free_energy( self ):
		os.chdir( self.path_to_the_full_system )
		struc = read( "OUTCAR" )
		system_with_H = struc.get_potential_energy()
		os.chdir( self.path_to_the_clean_substrate )
		struc = read( "OUTCAR" )
		clean_system = struc.get_potential_energy()
		total_grand_free_energy = ( system_with_H - clean_system  -  self.number_of_H * (  0.5* self.energy_H2 - self.SHE  - self.ln10KT * self.pH ) ) / self.area
		print( total_grand_free_energy )
		return total_grand_free_energy
		
if __name__ == "__main__":
	loc = "/home/theodoros/PROJ_ElectroCat/theodoros/HER/Pt/"
	for i in range( 0, 8 ):
		obj = Grand_Free_Energy( loc + "chg_0.0/1ML/target_potential", loc + "/chg_0.0/0ML/target_potential", loc + "H2", i )
		obj.get_grand_free_energy()
