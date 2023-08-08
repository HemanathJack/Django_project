#!/usr/bin/python3
"""Common function handlers for operations.
"""
import os
from concurrent.futures import ThreadPoolExecutor

class common_api:
	def dictionary_finder(self, dictionary, key_to_find):
		"""Recursively find key in dictionary that contains dictionaries.

	    Args:
	        dictionary (dict): Dict to search.
	        key_to_find: Key to find the value to.

	    Returns:
	        Value corresponding to key if found, else None.
	    """
		if isinstance(dictionary, dict):
			if key_to_find in dictionary:
				return dictionary[key_to_find]
			for value in dictionary.values():
				if isinstance(value, dict):
					return_value = self.dictionary_finder(value, key_to_find)
					if return_value is not None:
						return return_value
		return None
	
	def parallel_executing_functions(self, function_name, function_arg, workers=None):
		"""Parallel threading common function to run loop parallely

		Args:
			function_name (func): Function to execute parallely.
			function_args (list): Function arguments to iterate in loop.
			workers (int): Number of instances that run parallely. Defaults to None.

		Returns:
			Accumulate returnables of particular functions into list (list). 
		"""
		results = []
		with ThreadPoolExecutor(max_workers=workers) as executor:
			for result in executor.map(function_name, function_arg):
				results.append(result)
		return results

	def update_latest_branch(self, repository_location):
		"""Update latest repository branch from static location.

		Args:
			repository_location (str): Repository location in project static directory.
		"""
		#/Application/static/resources/iot/
		path = ''.join((os.getcwd(),f'{repository_location}'))
		os.chdir(path)
		os.system('git pull')
		back = '/'
		for times in range(len(repository_location.split('/'))-1):
			back = back +'../'
		os.chdir(''.join((os.getcwd(),back)))
