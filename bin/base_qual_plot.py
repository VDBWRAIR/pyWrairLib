#!/usr/bin/env python

from matplotlib import pyplot as plt
from pylab import *
import numpy as np
from argparse import ArgumentParser
import os.path

parser = ArgumentParser()
parser.add_argument( dest='inputfile', help='CSV File' )
args = parser.parse_args()

data = np.loadtxt( open( args.inputfile, "rb" ), delimiter=",", skiprows=1, usecols=(1,3,4) )

plt.plot( data )
plt.legend(['Min','Avg','Max'])
outputfile = os.path.splitext( args.inputfile )[0] + '.png'
savefig( outputfile )
