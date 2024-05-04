import Landau_Energy_library
import matplotlib.pyplot as plt

obj = Landau_Energy_library.Landau_Energy( pH_down = 0, pH_up = 7 )
V = obj.SHE_voltages
a = obj.get_Landau_energy_for_pH_7()

for i, j in a.items():
	print(i, j)

for coverage, energies in a.items():
    plt.plot( V, energies, "-o", label = coverage )

plt.xlabel(r'$\phi$ vs SHE')
plt.ylabel( 'Landau Energy' )
plt.legend( loc = "best" )
plt.show()
