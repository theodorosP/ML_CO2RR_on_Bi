#! /bin/bash

scp -rp -oHostKeyAlgorithms=+ssh-dss  theodoros@artemis.physics.cos.ucf.edu:/home/theodoros/PROJ_ElectroCat/theodoros/corrections/plotting/*.py .
