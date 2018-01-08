import os, sys

def read_data(nosta):
	data = open(nosta).readlines()
	mjd = data[3].split()[2].rstrip(',')
	for i in range(6):
		data.pop(0)
	for i in data:
		i=i.split()
		if float(i[4]) == 0 and float(i[7]) <3 and float(i[11])*float(i[12])*float(i[13])*float(i[14])*float(i[15])*float(i[16])==0:
			print mjd, i[0], i[1], i[2], i[3]
			
list = os.listdir('.')
list = filter(lambda x: x.startswith('PTF_20140107') and x.endswith('c00.nosta'), list)
a=map(read_data, list)
