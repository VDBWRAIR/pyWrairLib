#!/usr/bin/env python

from matplotlib import pyplot as plt
from pylab import *
import numpy as np
from argparse import ArgumentParser
import os.path

parser = ArgumentParser( description='Basic plot of base pair stats' )
parser.add_argument( dest='inputfile', help='CSV File generated from base_qual.py' )
args = parser.parse_args()

data = np.loadtxt( open( args.inputfile, "rb" ), delimiter=",", skiprows=1, usecols=(1,3,4) )

plt.plot( data )
plt.legend(['Min','Avg','Max'])
outputfile = os.path.splitext( args.inputfile )[0] + '.png'
savefig( outputfile )
