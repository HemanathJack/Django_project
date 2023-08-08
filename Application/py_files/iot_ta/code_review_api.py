#!/usr/bin/python3
"""Operation functions with API for code review tracking from scm.kone.com.
"""

from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from Application.py_files.common_lib.common import common_api
import requests

# Encrypted form of user credentials : USER >> Mohamed Jubair
CYPHER_KEY = bytes('oxdG8IdX72h7a9_IMbMbrja4bnCclctOpDImrjq1rLg=', 'utf-8') 
CYPHER = Fernet(CYPHER_KEY)

# Header keys | Company key and Account key for scm.
COMPANY_KEY_ENC = bytes('gAAAAABjnWjOnZZt7pDtaVQicn9EVm3VMUOQ1odK1MWwJyBIO830XN-VslOxBGotraABPbqShQicP73Xly874-4inrlcjsDnPJr9xVMNr2WKWKncMA1Zho7sCbV-aOaqz1hpwoLKocPn', 'utf-8')
ACCOUNT_KEY_ENC = bytes('gAAAAABjnWlhnPMDwIdzckAoB7ogujgLKKsGpBYATkpX8cWqL82emHuRhSWsvgHXZ2iKVIJD6VmjOl-ybzQ41i--73qRNcjVeaG3k1HJdN0d5Rxbo_MKX10qvMeC4x2JsaC4Zm6uR-xc', 'utf-8')

headers = { 'Authorization': f"company_key='{str(CYPHER.decrypt(COMPANY_KEY_ENC), 'utf-8')}',account_key='{str(CYPHER.decrypt(ACCOUNT_KEY_ENC), 'utf-8')}'"}
user_reviews = "https://scm.kone.com/api/projects/rellab/code_reviews?creator={}&limit=10000"


class codereview_api:
	"""API Function for code review functionalities
	"""
	def __init__(self):
		self.common = common_api()

	def get_weekend_counts(self, start_date, end_date):
		"""Get weekend counts with the given start and end date.

		Args:
			start_date (date): Start date.
			end_date (date): End date
		
		Returns:
			Number of weekend days. (int)
		"""
		day = timedelta(days=1)
		count_saturday = 0
		count_sunday = 0
		while start_date <= end_date:
			if start_date.isoweekday() == 6:
				count_saturday += 1
			if start_date.isoweekday() == 7:
				count_sunday += 1
			start_date += day
		return count_saturday + count_sunday

	def give_overall_status_of_user(self, user_id):
		"""Fetch data from scm.kone.com through API.

		Args:
			user_id (str): Username of user should match with scm kone id.
			date_format (str): Date format to convert. Defaults to "%Y-%m-%d"

		Returns:
			overall (dict): Overall code review status of specific user.
		"""
		date_format="%Y-%m-%d"
		
		response = requests.get(user_reviews.format(user_id), headers=headers)
		response = response.json()

		overall = dict()
		overall['total_cases'] = 0
		
		overall['open_cases'] = 0
		overall['merged_cases'] = 0
		overall['declined_cases'] = 0
		
		overall['min_standby'] = None
		overall['min_review_name'] = ''
		overall['max_standby'] = None
		overall['max_review_name'] = ''
		overall['fixbroken'] = 0
		overall['fixbroken_cases'] = list()

		rellab_iot = []
		for _review in response['results']:
			if _review['repository']['id'] == 'rellab_iot':
				if '[fixbroken]' in _review['title'].lower() or '[fix broken]' in _review['title'].lower():
					overall['fixbroken'] += 1
					overall['fixbroken_cases'].append(str(_review['id']) + ' ' + _review['title'])
				if _review['state'] == 'open':
					overall['open_cases'] += 1
				if _review['state'] == 'merged':
					overall['merged_cases'] += 1
					created_date = datetime.strptime(_review['created_at'].split('T')[0], date_format)
					updated_date = datetime.strptime(_review['updated_at'].split('T')[0], date_format)
					interval = updated_date - created_date
					interval = interval.days - self.get_weekend_counts(created_date, updated_date)
					if overall['min_standby']==None and overall['max_standby']==None:
						overall['min_standby'], overall['max_standby'] = interval, interval
						overall['min_review_name'], overall['max_review_name'] = str(_review['id']) + ' ' + str(_review['title']), str(_review['id']) + ' ' + str(_review['title'])
					else:
						if interval<overall['min_standby']:
							overall['min_standby'] = interval
							overall['min_review_name'] = str(_review['id']) + ' ' + str(_review['title'])
						if interval>overall['max_standby']:
							overall['max_standby'] = interval
							overall['max_review_name'] = str(_review['id']) + ' ' + str(_review['title'])

				if _review['state'] == 'closed':
					overall['declined_cases'] += 1
				overall['total_cases'] += 1
				rellab_iot.append(_review)
		# This condition is used as some reviews maybe created and pushed in weekends which results in negative value.
		if overall['min_standby'] < 0:
			overall['min_standby'] = 0
		overall['monthwise'] = self.month_and_year_wise_separation(rellab_iot)
		overall['all_max_reviews'] = self.list_all_reviews_more_than_days(rellab_iot)
		returnable = {user_id: overall}
		return returnable

	def return_overall_for_all_iot_users(self, user_object):
		"""Fetch overall code review status of all users of IOT TA team.
		
		Args:
			user_object (obj): User model from database SQLite3.

		Returns:
			iot_users (dict): IOT users overall code review results.
		"""
		iot_users = dict()
		_user_list = []
		for user in user_object.objects.all():
			if str(user) != 'admin' and user.team == 'IOT Test Automation':
				try:
					int(str(user))
					user = 'k'+str(user)
					_user_list.append(user)
				except:
					_user_list.append(user)
		iot_users_list = self.common.parallel_executing_functions(self.give_overall_status_of_user, _user_list)
		for dict_item in iot_users_list:
			iot_users = {**iot_users, **dict_item}

		return iot_users

	def month_and_year_wise_separation(self, data, date_format="%Y-%m-%d"):
		"""Code review month and year wise catagorization.
		
		Args:
			data (dict): Json response data from scm.kone.com.
			date_format (str): Date format to convert. Defaults to "%Y-%m-%d".

		Returns:
			period (dict): Monthwise catagorization.
		"""
		period = dict()
		period['max_days'] = dict()

		for _item in data:
			created_date = _item['created_at'].split('T')[0]
			dt = datetime.strptime(created_date, date_format)
			if str(dt.year) not in period:
				period[str(dt.year)] = 1
				period[str(dt.year)+'_months'] = dict()
			else:
				period[str(dt.year)] += 1
			if dt.strftime('%b') not in period[str(dt.year)+'_months']:
				period[str(dt.year)+'_months'][dt.strftime('%b')] = 1
			else:
				period[str(dt.year)+'_months'][dt.strftime('%b')] += 1

			updated_date = _item['updated_at'].split('T')[0]
			up_dt = datetime.strptime(updated_date, date_format)
			
			interval = (up_dt - dt).days
			interval = interval - self.get_weekend_counts(up_dt, dt)

			if str(dt.year) not in period['max_days']:
				period['max_days'][str(dt.year)] = dict()
			if str(dt.strftime('%b')) not in period['max_days'][str(dt.year)]:
				period['max_days'][str(dt.year)][str(dt.strftime('%b'))] = 0
				period['max_days'][str(dt.year)][str(dt.strftime('%b'))+'_title'] = None
			
			if _item['state'] == 'merged':
				if interval > period['max_days'][str(dt.year)][str(dt.strftime('%b'))]:
					period['max_days'][str(dt.year)][str(dt.strftime('%b'))] = interval
					period['max_days'][str(dt.year)][str(dt.strftime('%b'))+'_title'] = str(_item['id']) + ' ' + _item['title']
		return period

	def list_all_reviews_more_than_days(self, data, days=5, date_format="%Y-%m-%d"):
		"""Get all reviews that withstanded more than 5 days.
		
		Args:
			data (dict): code review api data of user to fetch about. 
			days (int): No. of days to filter. Defaults to 5.
			date_format (str): Date format to convert. Defaults to "%Y-%m-%d".

		Returns:
			review_data (dict): Code review title with interval dates.
		"""
		review_data = dict()
		for _item in data:
			created_date = _item['created_at'].split('T')[0]
			_cd = datetime.strptime(created_date, date_format)
			updated_date = _item['updated_at'].split('T')[0]
			_ud = datetime.strptime(updated_date, date_format)
			interval = (_ud - _cd).days
			interval = interval - self.get_weekend_counts(_ud, _cd)

			if interval > 5 and _item['state']=='merged':
				review_data[str(_item['id']) + ' ' + _item['title']] = interval
		return review_data
