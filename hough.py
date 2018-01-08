from numpy import *
from matplotlib import pyplot as plt
from scipy.spatial import KDTree
import sqlite3 as sq3
import sys

db_DIR = '.'
db_NAME = 'hough.db'
table_NAME = 'nonstationary3'

def create_table(): #Create a sqlite table
	conn = sq3.connect("%s/%s" %(db_DIR,db_NAME))
	cursor = conn.cursor()
	cursor.execute("""CREATE TABLE %s(ID text, RA real, DEC real, MJD real)""" %(table_NAME))
	cursor.close()
        
def insert_db(ID, RA, DEC, MJD): #generate the sql command
	sql =  'insert into %s values ("%s", %s, %s, %s)\n' %(table_NAME, ID, RA, DEC, MJD)
	return sql

def update_db(sql): #execute sql command
	sql = sql.split('\n')
	#print sql
	conn = sq3.connect("%s/%s" %(db_DIR,db_NAME))
	cursor = conn.cursor()
	map(cursor.execute,sql)      
	conn.commit()
	cursor.close()
    
def hough(x,y): #transfer x, y to hough space, return a list of r. The key of each element is the corresponding angle of r
	theta = (0.1*(array(range(10*90))+10*45)/180.*pi)
	r = x*cos(theta)+y*sin(theta)
	return r

def clean(ra,dec): #use two ann search to clean the stationary and non-paired detections
	tree = KDTree(zip(ra,dec))
	pair = tree.query_ball_tree(tree, 30/3600.)
	stationary = tree.query_ball_tree(tree, 1.5/3600.)
	mask = zeros(len(ra),dtype=bool)
	for n, i in enumerate(pair):
		if len(i) > 2 and len(stationary[n])==1:
			mask[n]= 1
		else:
			mask[n]= 0       
	return mask
    
def line(r_theta): #turn r and theta to a and b (y=ax+b)
	r, theta = r_theta
	a = -1/tan(theta*pi/180.)
	b = r/sin(theta*pi/180.)
	return a, b
    
def detect(ra, dec, MJD): #record the hough transfer result to database and histogram
	detection_r_theta = []
	sql =''
	hist = zeros([1000,900])
	for n, i in enumerate(zip(ra, dec)):
		r_theta = hough(i[0],i[1])		
		hist, sql = add_count(r_theta, hist, sql, i[0],i[1], MJD[n])
		if any(hist >= 15):
			#print 'detected!'
			detection_r_theta.append(zip(where(hist >=15)[0]/400.-1,where(hist >=15)[1]/10.+45)[0])
			hist[hist>=15] = 0
	return detection_r_theta, sql
		
def add_count(r_theta, hist, sql, ra, dec, MJD): #add count and sql command 
	for n, i in enumerate(r_theta):
		i=int(400*(i+1))
		hist[i][n]+=1
		ID = '%s_%s' %(i, n)
		sql += insert_db(ID, ra, dec, MJD)
	return hist, sql
    
def plot_line(a_b): #plot the line
	a,b = a_b
	x=arange(0,0.65, 0.01)
	y=a*x+b
	plt.scatter(x,y, c='r', marker='_')
    
    


if __name__ == "__main__":
	data = loadtxt('nonstationary3', dtype={'names':('ra', 'dec', 'mjd'), 'formats':('f4','f4', 'f8')})
	data = sort(data,  order='ra')[::-1]
	create_table()
	ra = data['ra']
	dec = data['dec']
	mjd = data['mjd']
	mask = clean(ra,dec)
	ra0 = ra[mask]
	dec0 = dec[mask]
	mjd = mjd[mask]
	ra = ra0-min(ra0)
	dec = dec0-min(dec0)
	result, sql = detect(ra, dec, mjd)
	update_db(sql)
	plt.scatter(ra,dec,marker='.')
	plot = map(plot_line, map(line, result))
	plt.show()
	
