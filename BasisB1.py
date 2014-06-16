import mechanize, json, os, datetime, pytz, csv
from bs4 import BeautifulSoup
from dateutil import rrule
import dateutil

class BasisB1:
	# --------------------------------------
	#			  Global Variables
	# --------------------------------------
	browser = mechanize.Browser() # Also look into potential of handling cookies for login sessions
	logged_in = False

	# --------------------------------------
	# 				CONSTRUCTOR
	# --------------------------------------
	def __init__(self, usr_name=None, pwd=None):
		# DEFAULT: Will only try to login, after initializing the BasisB1 object if 
		#		   usr_name and pwd are passed in
		if (pwd and usr_name):
			self.login(usr_name, pwd)

	# --------------------------------------
	#				LOGIN 
	# --------------------------------------
	def login(self, usr_name, pwd):
		# DEFAULT: Login functionality. usr_name and pwd should be string objects

		# Check that something is provided and if they are string objects
		if (not self.logged_in):
			if (usr_name and pwd):
				if (type(usr_name) != type("") and type(pwd) != type("")):
					usr_name = str(usr_name)
					pwd = str(pwd)
				try:
					self.browser.open("https://app.mybasis.com/login")
					response = self.browser.response() # Should check that connection worked at some point
					self.browser.select_form("loginform")
					self.browser["username"] = usr_name
					self.browser["password"] = pwd
					try:
						self.browser.submit() # Should also check that we login properly
						self.logged_in = True
					except Exception, e:
						print e.code
						print "SYSTEM INFO: Something went wrong in the login() submit()."
				except mechanize.HTTPError, e:
					print e.code
					print "SYSTEM INFO: Something went wrong in the login() using browser.open(). Check internet connection and url."
			else:
				print "SYSTEM INFO: No username or password specified"
		else:
			print "SYSTEM INFO: Already logged in."

	# --------------------------------------
	#	   API URL CALLS FOR V1 REST API
	# --------------------------------------	
	def set_V1_api_url(self, params=None, dates=[None, None]):
		# DEFAULT: Takes two optional parameters, params is a dict object (JSON), 
		#		   dates is a list of type ["YYYY-MM-DD", "YYYY-MM-DD"].
		# RETURNS: A string object containing the apropriate API call
		url = "https://app.mybasis.com/api/v1/chart/me?"
		if (not params):
			params = self.available_V1_metrics()
		if (dates == [None, None]):
			# Simply get today's dates
			dates = [datetime.date.today().strftime("%Y-%m-%d"), datetime.date.today().strftime("%Y-%m-%d")]
		if (type(params) != type({})):
			return ["SYSTEM INFO: Please make sure the input 'params' is a dictionary. See available_metrics() for specifics."]
		else:
			url += "start_date="+dates[0]+"&end_date="+dates[1]
			for key, val in params.iteritems():
				url += "&"+key+"="+val
			return url

	# --------------------------------------
	#			API CALL URL FOR V2
	# --------------------------------------
	# BELONGS TO: API V2
	# DEFAULT: Two optional arguments, activity = 'run,walk,bike' by default. May specify 'sleep'
	#		   Second argument is the date, specified as 'YYYY-MM-DD'
	#		   Right now, the Basis B1 API does not support to call run,walk,bike,sleep at the same time 
	# RETURNS: A string url of the requested API call for V2, default is today
	def set_V2_api_url(self, activity=None, date=None):
		if (date == None):
			date = datetime.date.today().strftime("%Y-%m-%d")
		if (type(date) == type("")):
			date = str(date) # Force type conversion
			url = "https://app.mybasis.com/api/v2/users/me/days/"+date+"/"
			if (activity == None):
				url += "activities?expand=activities&type=run,walk,bike"
				return url
			elif (activity == 'sleep'):
				url += "activities?expand=activities&type=sleep"
				return url
			else:
				return "SYSTEM INFO: Please specify a valid type; 'run,walk,bike' or 'sleep'."

		else:
			return "SYSTEM INFO: Please specify a valid date string, 'YYYY-MM-DD'."

	# --------------------------------------
	# 		REQUEST JSON DATA (V1 API)
	# --------------------------------------
	def request_json(self, api_url):
		# BELONGS TO: API V1, but should work regardless with any api_url pointing to a JSON object
		# DEFAULT: Takes a api_url, either as a list or as a string
		#		   Remember; if you have a short interval between data points, e.g. '60' and many days, it will take 
		#		   some time for the Basis server to aggregate the data and send back
		# RETURNS: JSON Data as a JSON object
		if (self.logged_in):
			try:
				if (type(api_url) == type("")):
					return json.loads((self.browser.open(api_url)).get_data())
			except ValueError, e:
				print "SYSTEM INFO: ", e.code
				return {"error": "Oops. Something went wrong with the JSON Decoding. Please check the login and API url."}
		else:
			return {"error": "SYSTEM INFO: Please log in before requesting any JSON data."}

	def request_user_info(self):
		# BELONGS TO: API V1
		# RETURNS: A JSON object containing specific user information
		base_api_url = "https://app.mybasis.com/api/v1/user/me.json"
		if (self.logged_in):
			try:
				return json.loads((self.browser.open(base_api_url)).get_data())
			except mechanize.HTTPError, e:
				print e.code
				return {"error": "SYSTEM INFO: Something went wrong with the API request. Please check that the Basis servers are running."}
		else:
			return {"error": "SYSTEM INFO: Please login before requesting user info."}

	def request_user_points(self):
		# BELONGS TO: API V1
		# RETURNS: A JSON object containing the number of gamified points the user has earned
		base_api_url = "https://app.mybasis.com/api/v1/points"
		if (self.logged_in):
			try:
				return json.loads((self.browser.open(base_api_url)).get_data())
			except mechanize.HTTPError, e:
				print e.code
				return {"error": "SYSTEM INFO: Something went wrong with the API request. Please check that the Basis servers are running."}
		else:
			return {"error": "SYSTEM INFO: Please login before requesting user points."}

	# --------------------------------------
	# 		 GET SPECIFIC BIOMETRICS
	# --------------------------------------
	def available_V1_metrics(self):
		# BELONGS TO: API V1
		# RETURNS: Available metrics in the API callback
		return { "heartrate": "true", 
				"skin_temp": "true",
				"gsr": "true",
				"calories": "true",
				"steps": "true",
				"summary": "true", 
				"interval": "60", 
				"start_offset": "0",
				"end_offset": "0",
				"bodystates": "true",
				"breaks": "0"
				}

	def extract_V1_metric(self, metric, json_data):
		# BELONGS TO: API V1
		# DEFAULT: Requires request_json() to have been called, takes two input parameters;
		#		   metric = string(), such as "heartrate", and json_data = {...}
		# RETURNS: A list of size n x 1 containing the metric values
		try:
			return json_data["metrics"][str(metric)]["values"]
		except TypeError, e:
			print e
			return ["SYSTEM INFO: Please check that the JSON input has a 'metrics' key."]

	# --------------------------------------
	# 	  GET ACTIVITIES AND TIMESTAMPS
	# --------------------------------------
	def extract_V1_bodystates(self, json_data, sort_by_start_time=False):
		# BELONGS TO: API V1
		# DEFAULT: Input is a json_data object, i.e. {}, 
		# 		   optional argument sort_by_start_time to activities by POSIX starttime timestamp
		# RETURNS: A Matrix (list of lists) containing the bodystates data in n x 3 dims
		#		   NOTE: The Matrix is not sorted by default, so beware.
		json_bodystates = json_data["bodystates"]
		if (sort_by_start_time):
			json_bodystates.sort(key=lambda x: x[0]) # Currently also moves the header to the bottom
		return json_bodystates

	def extract_V2_activities(self, json_data, sort_by_start_time=False):
		# BELONGS TO: API V2
		# DEFAULT: Input is a json_data object. Data is not sorted by default
		#		   Make sure that you are aware of the timezone for the POSIX timestamps
		# RETURNS: A matrix (list of lists) containing the activities type and data in the form 
		#		   [[type, calories, start_time, end_time], ...]
		json_activities = []
		for data in json_data["content"]["activities"]:
			json_activities.append([data.get("type"), data.get("calories"), data["start_time"].get("timestamp"), data["end_time"].get("timestamp")])
		if (sort_by_start_time):
			json_activities.sort(key=lambda x: x[2])
		return json_activities

	# --------------------------------------
	# 	  	   GET TIMEZONE HISTORY
	# --------------------------------------
	def extract_V1_timezone_history(self, json_data, asJSON=False):
		# BELONGS TO: API V1
		# DEFAULT: The JSON response is a mix of lists and dicts.  
		# RETURNS: Depending on optional argument, either a JSON object or a list
		if (asJSON == True):
			return json_data["timezone_history"][0]
		else:
			json_timezone = [["timezone", "gmt offset", "starttime"]] # list of lists
			tmp_list = []
			for key, val in json_data["timezone_history"][0].iteritems():
				tmp_list.append(val)
			json_timezone.append(tmp_list)
			return json_timezone

	# --------------------------------------
	# 			SAVE DATA TO FILE(S)
	# --------------------------------------
	def save_to_json(self, json_data, file_name):
		# BELONGS TO: API V1, but works with API V2 if a list [{}, ...] is provided
		# DEFAULT: Saves data to JSON format
		full_path_name = "./"+file_name+"_"+datetime.date.today().strftime("%Y-%m-%d")+".json"		
		if (not os.path.isfile(full_path_name)):
			with open(full_path_name, "wb") as file_to_save:
				json.dump(json_data, file_to_save, ensure_ascii=False)
				file_to_save.write("\n")
		else:
			with open(full_path_name, "a+b") as file_to_save:
				json.dump(json_data, file_to_save, ensure_ascii=False)
				file_to_save.write("\n") # To make things prettier	

	def save_V1_metrics_to_csv(self, json_data, file_name):
		# BELONGS TO: API V1
		# DEFAULT: Only specify the name of the file, without file extension, saves to relative dir "./"
		# 		   Only the values in json_data["metrics"] are saved, as we can compute summaries ourselves
		# NOTE: You may convert the skin temperature to Celsius yourself. Trivial!

		# TO DO: MAY REDO PARTS TO INCLUDE OPTIONAL HEADER FOR CSV FORMAT AND ENABLE V2 DATA TO BE SAVED

		# File name, including extension
		full_path_name = "./"+file_name+"_"+datetime.date.today().strftime("%Y-%m-%d")+".csv"

		# For convenience and readability only
		time_stamp = json_data["starttime"]
		time_step = json_data["interval"]
		h_list = json_data["metrics"]["heartrate"]["values"]
		s_list = json_data["metrics"]["steps"]["values"]
		c_list = json_data["metrics"]["calories"]["values"]
		sk_list = json_data["metrics"]["skin_temp"]["values"]
		gsr_list = json_data["metrics"]["gsr"]["values"]			
				
		if (not os.path.isfile(full_path_name)):
			with open(full_path_name, "wb") as file_to_save:
				csv.writer(file_to_save).writerow(["POSIX timestamp", "Heartrate", "Steps", "Calories", "Skin temperature (F)", "GSR"])
				for hr, s, c, sk, gsr in zip(h_list, s_list, c_list, sk_list, gsr_list):
					csv.writer(file_to_save).writerow([time_stamp, hr, s, c, sk, gsr])
					time_stamp += time_step
		else:
			with open(full_path_name, "a+b") as file_to_save:
				for hr, s, c, sk, gsr in zip(h_list, s_list, c_list, sk_list, gsr_list):
					csv.writer(file_to_save).writerow([time_stamp, hr, s, c, sk, gsr])
					time_stamp += time_step	