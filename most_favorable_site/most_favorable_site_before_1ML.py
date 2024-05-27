import re
import os
import matplotlib.pyplot as plt
from ase.io import read 

def get_correction_energy(outcar_path, keyword="GC Correction"):
    with open(outcar_path, "r") as file:
        for line in file:
            if keyword in line:
                correction_line = line
                break
    correction = re.findall(r'[-+]?\d*\.\d+|\d+', correction_line)
    return float(".".join(correction))

def get_potential_energies(base_path, chg_list, ml_list):
    energies = []
    for chg in chg_list:
        for ml in ml_list:
            path = os.path.join(base_path, chg, ml, "target_potential")
            os.chdir(path)
            print("Reading:", chg, ml)
            struc = read("OUTCAR")
            energies.append(struc.get_potential_energy())
    return energies

def plot_energies(x_values, y_values_list, labels, ymin, ymax, xticks, yticks, save_path, xlabel, ylabel):
    plt.figure(figsize=(3.5, 2.5))
    for y_values, label in zip(y_values_list, labels):
        plt.plot(x_values, y_values, marker='o', label=label)
    plt.xlabel(xlabel, fontsize=12, labelpad=0.5)
    plt.ylabel(ylabel, fontsize=12, labelpad=2)
    plt.ylim(ymin, ymax)
    plt.yticks(yticks, [str(y) for y in yticks])
    plt.xlim(x_values[0], x_values[-1])
    plt.xticks(xticks, [str(x) for x in xticks])
    plt.legend(loc="best")
    plt.subplots_adjust(left=0.18, right=0.98, top=0.99, bottom=0.17)
    plt.savefig(save_path, dpi=600)
    plt.show()

base_path = "/home/theodoros/PROJ_ElectroCat/theodoros/HER/Pt_fcc/testing_2"
outcar_path = "/home/theodoros/PROJ_ElectroCat/theodoros/HER/Pt_fcc/H2/OUTCAR"
path_save = os.getcwd()

chg_list = ["chg_0.0", "chg_-0.5", "chg_-1.0", "chg_-1.5", "chg_-2.0", "chg_-2.5"]
ml_groups = {
    "1ML": ["1ML_fcc", "1ML_top", "1ML_hcp"],
    "0.55ML": ["0.55ML_fcc", "0.55ML_top", "0.55ML_hcp"],
    "0.11ML": ["0.11ML_fcc", "0.11ML_top", "0.11ML_hcp"]
}

correction_energy = get_correction_energy(outcar_path)
struc = read(outcar_path)
ener_H2 = struc.get_potential_energy() - correction_energy

energies_dict = {}
for ml, structures in ml_groups.items():
    for structure in structures:
        energies_dict[structure] = get_potential_energies(base_path, chg_list, [structure])

x_values = [0, -0.5, -1.0, -1.5, -2.0, -2.5]
ymin, ymax = -390.5, -386.5
xticks = x_values
yticks = [-386, -388, -390]

plot_energies(
    x_values, 
    [energies_dict['1ML_fcc'], energies_dict['1ML_top'], energies_dict['1ML_hcp']], 
    ['1ML_fcc', '1ML_top', '1ML_hcp'], 
    ymin, ymax, xticks, yticks, 
    os.path.join(path_save, 'omega_before_1ML.png'), 
    r'$\Phi$ vs SHE', '$\Omega (eV)$'
)
