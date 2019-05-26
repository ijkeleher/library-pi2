# pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client httplib2
# python3 add_event.py --noauth_local_webserver

# Reference: https://developers.google.com/calendar/quickstart/python
# Documentation: https://developers.google.com/calendar/overview

# Be sure to enable the Google Calendar API on your Google account by following the reference link above and
# download the credentials.json file and place it in the same directory as this file.

from __future__ import print_function
from datetime import datetime
from datetime import timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools




class gcalender:
	def __init__(self):
		# If modifying these scopes, delete the file token.json.
		SCOPES = "https://www.googleapis.com/auth/calendar"
		store = file.Storage("token.json")
		creds = store.get()
		if(not creds or creds.invalid):
			flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
			creds = tools.run_flow(flow, store)
		self.service = build("calendar", "v3", http=creds.authorize(Http()))


	def insert(self, book_name = "Book"):
		date = datetime.now() # Borrow it from now
		next_week = (date + timedelta(days = 7)).strftime("%Y-%m-%d") # It's due in a week
		time_start = "{}T01:00:00+10:00".format(next_week)
		time_end = "{}T18:00:00+10:00".format(next_week)
		
		event = {
			"summary": "Library Book: " + book_name + " is due back :^)",
			"location": "RMIT Library",
			"description": book_name + " is due back",
			"start": {
				"dateTime": time_start,
				"timeZone": "Australia/Melbourne",
			},
			"end": {
				"dateTime": time_end,
				"timeZone": "Australia/Melbourne",
			}
		}

		print("Inserting reminder event into calender")
		event = self.service.events().insert(calendarId = "primary", body = event).execute()
		print("Event created: {}".format(event.get("htmlLink")))
		print("Event id: {}".format(event.get("id")))

		return event.get("id")

	def delete(self, event_id):
		delete = self.service.events().delete(calendarId = "primary", eventId = event_id).execute()

