import urllib2
import requests
from requests.auth import HTTPBasicAuth

url = "http://localhost:5000/"
requests.get(url, auth=('miguel', 'python'))
html = urllib2.urlopen(url)

"""NEED TO TALK TO OUR APP TO DO ALL NECESSARY THINGS WITHOUT BROWSER RENDERINGS. 
HOW REQUEST THINGS FROM OUR SERVER AND PASS CREDENTIALS? ONCE, OR WITH EACH REQUEST?
CAN WE USE CURL WITHIN A PROGRAM? 
ALSO NEED TO PASS THE TEXT THAT NEEDS PROCESSED."""
