import pandas as pd
from ase.io import read
import matplotlib.pyplot as plt
import os

def get_energy(base_path, coverage):
    energies = []
    charges = [0.0, -0.5, -1.0, -1.5, -2.0, -2.5]
    for charge in charges:
        charge_path = os.path.join(base_path, f"chg_{charge:.1f}", coverage, "target_potential")
        os.chdir(charge_path)
        struc = read("OUTCAR")
        energies.append(struc.get_potential_energy())
    return energies

def collect_energies(base_path, coverages):
    energy_data = {}
    for coverage in coverages:
        energy_data[coverage] = get_energy(base_path, coverage)
    return energy_data

loc_top = "/storage/proj2/ElectroCat/theodoros/HER/Pt_hol/"
loc_fcc = "/storage/proj2/ElectroCat/theodoros/HER/Pt_fcc/"
loc_fcc_hcp = "/storage/proj2/ElectroCat/theodoros/HER/Pt_fcc_hcp/"

coverages_all = ["1.11ML", "1.22ML", "1.33ML", "1.44ML", "1.55ML", "1.66ML", "1.77ML", "1.88ML", "2ML"]
coverages_partial = ["1.11ML", "1.44ML", "1.88ML", "2ML"]

omega_top = collect_energies(loc_top, coverages_all)
omega_fcc = collect_energies(loc_fcc, coverages_all)
omega_fcc_hcp = collect_energies(loc_fcc_hcp, coverages_partial)

columns = ['chg_0.0', 'chg_-0.5', 'chg_-1.0', 'chg_-1.5', 'chg_-2.0', 'chg_-2.5']
index1 = [f"{cov}_top" for cov in coverages_all]
index2 = [f"{cov}_fcc" for cov in coverages_all]
index3 = [f"{cov}_fcc_hcp" for cov in coverages_partial]

structured_data = {
    col: [omega_top[cov][i] for cov in coverages_all for i, col_ in enumerate(columns) if col == col_] +
         [omega_fcc[cov][i] for cov in coverages_all for i, col_ in enumerate(columns) if col == col_] +
         [omega_fcc_hcp[cov][i] for cov in coverages_partial for i, col_ in enumerate(columns) if col == col_]
    for col in columns
}

df = pd.DataFrame(structured_data, index=index1 + index2 + index3)

print(df)

state_l = 0.9
state_h = 3
m_left, m_right, m_bottom, m_top = 0.18, 0.98, 0.17, 0.99
plt_h, plt_w = 2.5, 3.5

fig, ax2 = plt.subplots(figsize=(plt_w, plt_h))

x_values = [0, -0.5, -1.0, -1.5, -2.0, -2.5]
x_values_new = [-1.0, -1.5, -2.0, -2.5]
ymin, ymax = -415.5, -411.5
yticks = [-412, -413, -414, -415]
xticks = [0, -0.5, -1.0, -1.5, -2.0, -2.5]

ax2.set_xlabel(r'$\Phi$ vs SHE', fontsize=12, labelpad=0.5)
ax2.set_ylabel('$\Omega (eV)$', fontsize=12, labelpad=2)
ax2.set_ylim(ymin, ymax)
ax2.set_yticks(yticks)
ax2.set_yticklabels(map(str, yticks))
ax2.set_xlim(-2.6, 0.1)
ax2.set_xticks(xticks)
ax2.set_xticklabels(map(str, xticks))
ax2.hlines(0, -0.2, 0.1, lw=0.5, color='gray')

ax2.plot(x_values, df.loc["1.88ML_top"], "-o", label="1ML:H top + H on fcc, 1.88ML")
ax2.plot(x_values, df.loc["1.88ML_fcc"], "-o", label="1ML:H fcc + H on top, 1.88ML")
ax2.plot(x_values_new, df.loc["1.88ML_fcc_hcp"][2:], "-o", label="1ML:H fcc + H on hcp, 1.88ML")

fig.subplots_adjust(left=m_left, right=m_right, top=m_top, bottom=m_bottom, wspace=0.00, hspace=0.0)
ax2.legend(loc="best")

path_save = os.getcwd()
plt.savefig(os.path.join(path_save, 'omega_after_1ML.png'), dpi=600)
plt.show()
