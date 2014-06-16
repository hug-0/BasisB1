# ----------------------------------------------
# IMPORTING THE PACKAGE FOR USE
# ----------------------------------------------
from BasisB1 import *

# ----------------------------------------------
# CREATE AN INSTANCE OF THE BASIS B1 AND LOGIN
# ----------------------------------------------
basis = BasisB1(usr_name="email", pwd="password")

# ----------------------------------------------
# YOU MAY ALSO OVERRIDE THE CONSTRUCTOR LATER ON
# AND CHECK IF YOU ARE LOGGED IN
# ----------------------------------------------
basis.login("cmpjmi@gmail.com", "robertbosch11")
basis.logged_in # TRUE/FALSE

# ----------------------------------------------
# IT'S EASY TO FETCH THE USER INFORMATION
# ----------------------------------------------
user_info = basis.request_user_info()
user_points = basis.request_user_points()

# ----------------------------------------------
# THERE ARE 2 DIFFERENT APIs THAT MAY BE CALLED
# THE FIRST ONE IS CALLED V1, THE SECOND V2.
# THE BASIS SERVER RESPONSES ARE DIFFERENT 
# DEPENDING ON WHICH API IS USED, SO THERE ARE 
# DIFFERENT METHODS IMPLEMENTED TO HANDLE THIS
# ----------------------------------------------

# ----------------------------------------------
# THE V1 API SETTER TAKES TWO OPTIONAL ARGUMENTS
# BY DEFAULT, TODAY'S DATA URL IS CREATED, BUT
# YOU MAY ALSO SPECIFY THE START AND END DATES
# AS WELL AS WHICH REST PARAMETERS YOU WANT TO
# CALL. V2 ALSO HAS TWO OPTIONAL ARGUMENTS
# ----------------------------------------------
api_V1_url = basis.set_V1_api_url(dates=["2014-02-23","2014-02-24"], params=None)
api_V2_url = basis.set_V2_api_url(date='2014-02-21', activity="sleep")

# ----------------------------------------------
# YOU REQUEST JSON DATA LIKE SO:
# WORKS WITH BOTH THE V1 AND V2 OF THE API
# ----------------------------------------------
json_metrics = basis.request_json(api_V1_url)
json_activities = basis.request_json(api_V2_url)

# ----------------------------------------------
# THE PARAMETERS PASSED INTO V1 API URL SETTER
# CAN BE GOTTEN LIKE SO:
# ----------------------------------------------
available_metrics = basis.available_V1_metrics()

# ----------------------------------------------
# YOU MAY EASILY EXTRACT A SPECIFIC BIOMETRIC
# FROM THE BASIS B1 SERVERS, SIMPLY PASS THE
# RELEVANT 'METRIC' AS AN ARGUMENT
# ----------------------------------------------
heartrate = basis.extract_V1_metric("heartrate", json_metrics)
steps = basis.extract_V1_metric("steps", json_metrics)

# ----------------------------------------------
# YOU MAY WANT TO GRAB THE EXACT BODY STATES
# AT DIFFERENT POINTS IN TIME, OVER A TIMEPERIOD
# OR SIMPLY OVER ONE DAY...
# ----------------------------------------------
bodystates = basis.extract_V1_bodystates(json_metrics, sort_by_start_time=True)

# ----------------------------------------------
# ...OR SPECIFIC ACTIVITIES FROM A CERTAIN DAY
# ----------------------------------------------
activities = basis.extract_V2_activities(json_activities, sort_by_start_time=True)

# ----------------------------------------------
# IF YOU WANT SPECIFIC TIMEZONE INFORMATION
# FROM A SPECIFIC PERIOD OF TIME, LIST OR JSON
# ----------------------------------------------
timezone_history = basis.extract_V1_timezone_history(json_metrics, asJSON=True)

# ----------------------------------------------
# SAVING TO A JSON FILE IS ALSO EASY.
# SAVES TO RELATIVE ./ DIRECTORY
# ----------------------------------------------
basis.save_to_json(json_metrics, "metrics_file")
basis.save_to_json(json_activities, "activities_file")
basis.save_V1_metrics_to_csv(json_metrics, "csv_name")




