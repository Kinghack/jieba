#Noah Rubin
#06/26/2014
#Flaskr_blogapp.py
# check MVC model for a web project
# seprate different function in to different file, not in one file.
# what's the difference between analyse and KNserver/flaskr/jieba/analyse? Try to reorginize the project
# remove all the file with suffix *.*~ by add all this file type in .gitignore

#import necessary libraries and methods
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import jieba
import json
import urllib2
from updatedCities import citiesDict, getCitiesHTML, parseCitiesWhile
import chardet

#From Miguel Gringberg
from flask import Flask, jsonify, abort, request, make_response, url_for
from requests.auth import HTTPBasicAuth

#Launch  "cronjob" python function to retreive updated cities list
getCitiesHTML()
parseCitiesWhile()

"""pragma mark createApp"""

#create the application and configure - note for bigger applications, configuration should be done in separate module
app = Flask(__name__)
app.config.from_object(__name__)
#For verification 
auth = HTTPBasicAuth()

app.config.update(dict(DATABASE = os.path.join(app.root_path, 'flaskr.db'), DEBUG = False, SECRET_KEY = 'baixing_jieba'))
app.config.from_envvar('FLASKR_SETTINGS', silent = True)

#config object like a dictionary, can add new values like a dic
#app.rooth_path attribute used to find the path of the app, useful to maintain concurrency safe code
#environment specific configuration files advised, so can use from_envvar(). Define FLASKR_SETTINGS var that points to config file to be loaded. Silent says don't complain if no var exists
#can also use from_object() and config object from module provided will be loaded. Only uppercase var names included
#SECRET_KEY is to keep client-side sessions secure.  Make complex and hard to guess

@auth.get_password
def get_password(username):
	if username == 'miguel':
		return 'python'
	return None

@auth.error_handler
def unauthorized():
	
	return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
	# return 403 instead of 401 to prevent browsers from displaying the default auth dialog

# two not_found function?
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify( { 'error': 'Bad request' } ), 400)
 
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify( { 'error': 'Not found' } ), 404)

"""pragma mark Database and Application Context"""

@auth.login_required
def connect_db():
	"""Connects to the database
	Uses sqlite3.Row object to represent rows - treat rows
	as dictionaries rather than tuples"""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

@auth.login_required
def get_db():
	"""Opens a new database connection if there is not one open yet for 
	current application context"""
	if not hasattr(g,'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@auth.login_required
@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of request
	Tears down the app """
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@auth.login_required
def init_db(): 
	"""Creates the application context before request is sent
	Without application context, g object (where store information) does
	now know which context to become"""
	with app.app_context(): #establishes application context
		db = get_db() 
		with app.open_resource('schema.sql', mode = 'r') as f: #opens resource provided by app
			db.cursor().executescript(f.read()) #executes the schema.sql script to create database
		db.commit() #commit the changes -- teardown functions executed afterward

"""pragma mark View Functionality"""
@auth.login_required
@app.route('/')
def show_entries():
	"""Populates view with entries from database,
	passes entries to show_entries template and renders"""
	session.clear()
	db = get_db()
	cur = db.execute('select proc, text from entries order by id desc') 
	latest = cur.fetchone()
	entries = cur.fetchall()
	noahsMoms = [{'id': 1, 'description': 'hot', 'name': 'Shiela'}, {'id': 2, 'description': 'nahh', 'name': 'Jessica'}]
	#return render_template('show_entries.html', latest=latest, entries=entries)
	return jsonify( { 'Noahs moms': noahsMoms } )

#Makes citiesDict available to all templates
@auth.login_required
@app.context_processor
def inject_citiesDict():
	"""Passes the cities dictionary to application context"""
	global citiesDict
	return dict(citiesDict = citiesDict)

# why should we insert db here?
@auth.login_required
@app.route('/process', methods = ['POST'])
def process_words():
	"""Processes text input and JSON dumps entry to the database"""
	db = get_db()
	seg_list = jieba.cut_for_search(request.form['text']) #initializes trie
	output = " / ".join(seg_list)
	joutput = json.dumps(output)
	db.execute('insert into entries (text, proc) values (?,?)', [request.form['text'], joutput])
	db.commit()
	return redirect(url_for('show_entries'))

@auth.login_required
@app.route('/addWords', methods = ['POST'])
def addToDictionary():
	"""Grabs list of checked words and adds to the operating dictionary
	Note: If word already exists in dictionary, increments frequency"""
	wordList = request.form.get('segCheckbox')
	for word in wordList:
		jieba.add_word(word,1)
	flash("You successfully updated the dictionary!")
	return redirect(url_for('show_entries'))

@auth.login_required
@app.route('/updateDictionary', methods = ['POST'])
def updateDictionary():
	"""Changes the operating dictionary based on user choice on web"""
	city = request.form.get("cityContainer")
	category = request.form.get("categoryContainer")
	#jieba.set_dictionary('/home/noah/jieba/KNserver/flaskr/jieba/dictionaries/%(cityVar)s/%(cityVar)s_%(categoryVar)s.txt' % \ {'cityVar':city, 'catVar':category})
	print "Operating dictionary is: " + str(jieba.get_abs_path_dict())
	return redirect(url_for('show_entries'))

@auth.login_required
@app.route('/queryDictionary', methods = ['GET', 'POST'])
def queryDictionary():
	"""Adds queried word to session dictionary and renders the
	query dictionary page"""
	try:
		queriedWord = session['queriedWord'].decode('utf-8')
		queriedWordFrequency = session['queriedWordFrequency'].decode('utf-8')
	except:
		queriedWord = ''
		queriedWordFrequency = ''
	return render_template('Query_Dictionary.html', queriedWord=queriedWord, queriedWordFrequency=queriedWordFrequency)

@auth.login_required
@app.route('/sendQuery', methods = ['GET', 'POST'])
def sendQuery():
	"""Processes user query and sets session vars for word and frequency.
	Values are accessed with keys queriedWord and queriedWordFrequency"""
	query = request.form.get('query') #might have to fix encoding, keep in mind! look for decoding error
	dictionary = open(jieba.get_abs_path_dict())
	dictArray = _searchDictionary(dictionary, query)
	try:
		session['queriedWord'] = dictArray[0]
		session['queriedWordFrequency'] = dictArray[1]
	except:
		print "Not found"
	return redirect(url_for('queryDictionary'))


''' pragma mark Helper Functions '''
@auth.login_required
def _searchDictionary(dictionary, query):
	"""Helper function: searches the dictionary text file for
	given query, returns array with format [word,frequency] or empty
	dictionary.  Note: if line has improper encoding will not be searched"""
	for line in dictionary:
		encodingDict = chardet.detect(line)
		print encodingDict
		encoding = encodingDict['encoding']
		try:
			line = unicode(line, encoding)
			if query in line:
				ind = line.find(' ')
				word = line[0:ind]
				if query == word:
					print "Found it"
					ind2 = line.rfind(' ')
					frequency = line[ind+1:ind2]
					return [word.encode('utf-8'),frequency.encode('utf-8')]
		except:
			print "I failed to decode: " + encoding
			pass
	return []


if __name__ == '__main__':
	app.run(host="0.0.0.0")







