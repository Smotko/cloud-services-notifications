#!/usr/bin/python
# -*- coding: utf-8 -*-

# gmailatom 0.0.1
#
# HOW TO USE:
# 1) Create an instance of 'GmailAtom' class. The two arguments
#    its constructor take are the username (including '@gmail.com')
#    and the password.
# 2) To retrieve the account status call 'refreshInfo()'.
# 3) To get the unread messages count call 'getUnreadMsgCount()'.
#    You MUST call 'refreshInfo()' at least one time before using
#    this method or it will return zero.
# 4) To get specific information about an unread email you must
#    call the corresponding getter method passing to it the number
#    of the message. The number zero represents the newest one.
#    You MUST call 'refreshInfo()' at least one time before using any
#    getter method or they will return an empty string.
#    The getter methods are:
#	getMsgTitle(index)
#	getMsgSummary(index)
#	getMsgAuthorName(index)
#	getMsgAuthorEmail(index)
#
# by Jesús Barbero Rodrígez
# juan.grande@gmail.com

from xml.sax.handler import ContentHandler
from xml import sax
import urllib2
import re
import urllib
import xml.dom.minidom

class Mail:
	title=""
	summary=""
	author_name=""
	author_addr=""

# The mail class
class GreaderAtom:
	
	login_url = "https://www.google.com/accounts/ServiceLogin"
	auth_url = "https://www.google.com/accounts/ServiceLoginAuth"
	reader_url = "https://www.google.com/reader/api/0/unread-count"
	
	def __init__(self, user, pswd):
		self.username = user
		self.password = pswd
		# initialize authorization handler
		_cproc = urllib2.HTTPCookieProcessor()
		self.opener = urllib2.build_opener(_cproc)
		urllib2.install_opener(self.opener)

	def sendRequest(self):
		f = urllib2.urlopen(self.login_url)
		data = f.read()
		galx_match_obj = re.search(r'name="GALX"\s*value="([^"]+)"', data, re.IGNORECASE)
		galx_value = galx_match_obj.group(1) if galx_match_obj.group(1) is not None else ''
		params = urllib.urlencode({'Email':self.username,
					'Passwd':self.password,
					'GALX':galx_value})
			   
		f = urllib2.urlopen(self.auth_url, params)

		return self.opener.open(self.reader_url)

	def parseDocument (self, data):
		self.feeds=list()

		def processObject (ob):
			for c in ob.getElementsByTagName ("string"):
				if c.getAttribute("name") == "id":
					ftype, s, feed = c.childNodes[0].nodeValue.partition("/")
					self.feeds.append({"type" : ftype,
							   "feed" : feed})
					break
			
			for c in ob.getElementsByTagName ("number"):
				if c.getAttribute("name") == "count":
					self.feeds[-1]["count"] = c.childNodes[0].nodeValue
					break
		
		doc = xml.dom.minidom.parseString(data)
		elist = doc.childNodes[0].getElementsByTagName("list")[0]
		for e2 in elist.getElementsByTagName("object"):
			processObject (e2)

	def refreshInfo(self):
		self.parseDocument (self.sendRequest().read())

	def getTotalUnread(self):
		count = 0
		for feed in self.feeds:
			if feed["type"] == "user":
				name = feed["feed"]
				name = name[name.rfind ("/") + 1:]
				if name == "reading-list":
					count = feed["count"]

		return count