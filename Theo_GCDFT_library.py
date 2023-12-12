from ase.io import read 
import re
from dlePy.vasp.getdata import get_energy
import os
import matplotlib.pyplot as plt


def get_NELECT_duy( outcar ):
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



def get_NELECT_current_pot_energy():
	word_1 = "UPDATED NELECT"
	word_2 = "FERMI_SHIFT         ="
	word_3 = "CURRENT POTENTIAL   ="
	word_4 = "EFERMI              ="
	struc = read("OUTCAR")
	energy = struc.get_potential_energy()
	with open("OUTCAR", "r") as file:
		for line_number, line in enumerate(file):
			if word_1 in line:
				NELECT_all = line
			if word_2 in line:
				fermi_shift_all = line
			if word_3 in line:
				current_potential_all = line
			if word_4 in line:
				fermi_energy_all = line
	fermi_energy_1 = fermi_energy_all.replace("    EFERMI              = ", "")
	fermi_energy_2 = fermi_energy_1.replace("eV", "")
	fermi_energy = float(fermi_energy_2)
	NELECT_1 = NELECT_all.replace("UPDATED NELECT      =", "")
	NELECT_2 = NELECT_1.replace("electrons", "")
	NELECT  = float(NELECT_2)
	current_potential_1 = current_potential_all.replace("    CURRENT POTENTIAL   =  ", "")
	current_potential_2 = current_potential_1.replace(" V [= -(EFERMI + FERMI_SHIFT)] \n", "")
	current_potential = float(current_potential_2)
	#print("current_potential_all = ", current_potential_all)
	fermi_shift_1 = fermi_shift_all.replace("    FERMI_SHIFT         =  ", "")
	fermi_shift_2 = fermi_shift_1.replace(" eV\n", "")
	fermi_shift = - float(fermi_shift_2)
	return  fermi_shift, current_potential, NELECT, energy, fermi_energy


def parse_outcar( outcar ):
	ENERGY = get_energy( outcar )
	with open( outcar, 'r' ) as f:
		lines = f.readlines( )
	for il in range( len( lines ) - 1, -1, -1 ):
		if 'CURRENT NELECT      =' in lines[ il ]:
			cNELECT = float( lines[ il ].split()[-2] )
		if 'CURRENT POTENTIAL   =' in lines[ il ]:
			phi = float( lines[ il ].split('=')[1].split()[0] )
		if 'FERMI_SHIFT         =' in lines[ il ]:
			phi_vac = -float( lines[ il ].split()[-2] )
			break
	return phi_vac, phi, cNELECT, ENERGY


def calc_omega_supl( outcar_q ):
	print("Please wait...")
	data_q = parse_outcar( outcar_q )
	NELECT = get_NELECT_duy( outcar_q )
	q = NELECT - data_q[ 2 ]
	phi_vac = data_q[ 0 ]
	phi = data_q[ 1 ]
	omega = data_q[ 3 ] + q * phi_vac - q * phi
	return omega


def calc_omega():
	data = get_NELECT_current_pot_energy_theo()
	print("Please wait...")
	NELECT = get_NELECT_duy("OUTCAR")
	q = NELECT - data[ 2 ]
	phi_vac = data[ 0 ]
	phi = data[ 1 ]
	omega = data[ 3 ] + (NELECT - data[2]) * data[4]
	return omega


def binding_energy(system_full, system_truncated, voltage, en_box):
	omega = list()
	omega_full = list()
	omega_truncated = list()
	for i in voltage:
		os.chdir(path_to_folder)
		omega_full.append(calc_omega_theo())
	for i in voltage:
		os.chdir(path_to_folder)
		omega_truncated.append(calc_omega_theo())
	for i in range(len(omega_full)):
		omega.append((omega_full[i] - omega_truncated[i] - 2*en_box)/2)
	print("omega " + system_full, omega)
	return omega




