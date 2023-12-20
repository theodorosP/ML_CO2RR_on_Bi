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
