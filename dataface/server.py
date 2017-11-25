from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import flask_login
import time
import MySQLdb
import ConfigParser

# //YYYY-MM-DD HH:MM:SS

app = Flask(__name__)
Bootstrap(app)

dbcreds = ConfigParser.ConfigParser()
dbcreds.read('db.cfg')
db = MySQLdb.connect(host=dbcreds.get('database', 'host'),
                     user=dbcreds.get('database', 'user'),
                     passwd=dbcreds.get('database', 'passwd'),
                     db=dbcreds.get('database', 'db'))

last_update_dict = {} 

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == "POST":
		if request.form['MAC'] in last_update_dict:
			if (time.time() - last_update_dict[request.form['MAC']]) < 300:
				return "Too Many Requests."
		else:
			cur = db.cursor()
			cur.execute("SELECT deviceID,deviceType,MAC FROM Devices WHERE deviceType=" + request.headers.get(['User-Agent']) + " AND MAC=" + request.form['MAC'])
		##Get device info from database
		##Verify device, time
		##Update Data 

		with open('data', 'a') as f:
			f.write("--- POST FROM " + str(request.headers.get('User-Agent')) + " ---" + time.strftime("%H:%M:%S") + "\n")
			f.write(str(request.form) + "\n")
			for key in request.form:
				f.write("  " + str(key) + " - " + str(request.form[key]) + "\n")
                        print(str(request.headers))
                        print(str(request.form) + "\n\n")
		return "<html><body>Success!</body></html>"
	else:
		return render_template('index.html')

@app.route('/map')
def map():
	location_info = []
	cur = db.cursor()
	cur.execute("SELECT deviceID,name,descr,lat,lon FROM  Devices")
	for row in cur.fetchall():
	    location_info.append({
	    	'id':row[0],
	    	'name':row[1], 
	    	'varname':row[1].replace(' ', '_'), 
	    	'coords':{'lat':row[3], 'lon':row[4]}, 
	    	'desc':row[2]
	    })
	return render_template('map.html', location_info=location_info)

@app.route('/manage')
def manage():
	return render_template('manage.html')

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
	if request.method == "POST":
		cur = db.cursor()
		deviceID = 0
		cur.execute("SELECT deviceID FROM Devices ORDER BY deviceID desc limit 1")
		for row in cur.fetchall():
			deviceID = int(row[0]) + 1
		insert_string = "INSERT INTO Devices (deviceID, deviceType, name, descr, lat, lon, MAC) VALUES ("
		insert_string += str(deviceID) + ","
		insert_string += "\"" + str(request.form['deviceType']) + "\","
		insert_string += "\"" + str(request.form['name']) + "\","
		insert_string += "\"" + str(request.form['descr']) + "\","
		insert_string += str(request.form['lat']) + ","
		insert_string += str(request.form['lon']) + ","
		insert_string += "\"" + str(request.form['MAC']) + "\""
		insert_string += ")"
		print insert_string
		cur.execute(insert_string)
		db.commit()
		return "Success"
	elif request.method == "GET":
		return render_template('display_add_device.html')

@app.route('/login')
def login():
	return 0

