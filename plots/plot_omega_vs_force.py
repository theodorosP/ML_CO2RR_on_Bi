rom get_data_for_plotting import *
import matplotlib.pyplot as plt

obj = forces()
df = obj.get_plotting_dataframe()

systems_plot = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

legend_font = 8
labelpadx = 0.5
labelpady = 0.5
tick_font = 10
axis_font = 12
plt_h = 2.5
plt_w = 3.5
dpi = 600
m_left = 0.18
m_right = 0.98
m_bottom = 0.17
m_top = 0.99

labels = {}
labels[ 0 ] = { 'name':r'no cation', 'offset' : (-0.005, 0.007 ) }
labels[ 1 ] = { 'name':r'Na$^{+(1)}$', 'offset' : (-0.004, 0.007 ) }
labels[ 2 ] = { 'name':r'Na$^{+(2)}$', 'offset' : (0, 0.007 ) }
labels[ 3 ] = { 'name':r'NH$_4^{+(1)}$', 'offset' : ( -0.008, -0.03 ) }
labels[ 4 ] = { 'name':r'NH$_4^{+(2)}$', 'offset' : (0.002,  -0.03 ) }
labels[ 5 ] = { 'name':r'CH$_3$NH$_3^{+(1)}$', 'offset' : (-0.002, 0.007 ) }
labels[ 6 ] = { 'name':r'CH$_3$NH$_3^{+(2)}$', 'offset' : (-0.013, 0 ) }
labels[ 7 ] = { 'name':r'CH$_3$NH$_3^{+(3)}$', 'offset' : (0, 0 ) }
labels[ 8 ] = { 'name':r'(CH$_3$)$_4$N$^{+(1)}$', 'offset' : (-0.004, 0.02 ) }
labels[ 9 ] = { 'name':r'(CH$_3$)$_4$N$^{+(2)}$', 'offset' : (-0.015, 0.01 ) }

fig = plt.figure(figsize=(plt_w,plt_h))
ax2 = fig.add_subplot(1, 1, 1 )
ax2.plot(df["Omax"], df["Omega"], "o", markersize = 4)

for i, txt in enumerate(systems_plot):
    x = df["Omax"][i] + labels[ i ][ 'offset' ][ 0 ]
    y = df["Omega"][i] + labels[ i ][ 'offset' ][ 1 ]
    ax2.text( x, y, labels[ i ][ 'name' ], fontsize = 8 )

xmax = 0.06
xmin = -0.01
ymax = 0.2
ymin = -0.3
ax2.set_xlabel(r'$F_\mathrm{Ion-O}$ (eV/$\mathrm{\AA}$)', fontsize = 10, labelpad = 1)
ax2.set_ylabel('$\Delta\Omega_{ads}$ (eV)', fontsize = axis_font, labelpad = labelpady )
ax2.set_ylim( ymin, ymax)
yticks =  [-0.3, -0.2, -0.1, 0.0, 0.1 ] 
ax2.set_yticks( yticks )
ax2.set_yticklabels( [ str(x) for x in yticks ] )
ax2.set_xlim( xmin, xmax)
xticks =  [ 0, 0.01, 0.02, 0.03, 0.04] 
ax2.set_xticks( xticks )
ax2.set_xticklabels( [ str( x ) for x in xticks ] )
ax2.hlines(0, xmin, xmax, lw = 0.5, color = 'gray' )
ax2.text(xmin + 0.001,  ymin +0.01 , '$\Phi$ = -1.4 (V vs RHE)', fontsize = 9)
plt.subplots_adjust(left=m_left, right=m_right, top=m_top, bottom=m_bottom, wspace=0.00, hspace= 0.0 )
plt.savefig( 'force_vs_BE.png', dpi = 600 )
plt.show()
