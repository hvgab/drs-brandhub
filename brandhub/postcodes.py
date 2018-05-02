
import requests
import pprint
import pymssql
import logging
import os
import datetime as dt
from .config import CompanyID
import json

pp = pprint.PrettyPrinter()

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class Postcodes(object):
	"""docstring for Brandhub_Postcodes."""
	def __init__(self):
		logger.debug('init')
		self.last_updated = None
		self.raw_file_path = None
		self.formatted_file_path = None


	def search(self, postcode, _from='file'):
		""" Search for postcode

			from = ['file', 'db', 'live']
		"""

		if _from == 'file':
			self.search_file(postcode)


	def search_file(self, postcode):
		""" Search for postcode """
		if not self.formatted_file_path:
			self.update_files()
		with open(self.formatted_file_path) as po_file:
			postcodes = json.load(po_file)

		postcode = int(postcode)
		# Item = [postcode, timeblock1, timeblock2, timeblock3]
		for item in postcodes:
			if item[0] == postcode:
				return item

	def get(self, companyId):
		""" get and return from api """
		payload={'companyId':companyId}
		r = requests.get(os.getenv('BRANDHUB_POSTALCODES_URL'), params=payload)
		logger.debug(f'Statuscode {r.status_code}')
		return r.json()

	def reformat(self, postcodes):
		""" reformaterer api resultatet til liste av tuples """

		# return this
		postcode_list = []

		for item in postcodes['postalcodes']:
			# create new formatted postcode object.
			postcode = {}
			postcode['code'] = item['code']
			for i in range(1, 4):
				# Need an item for timeblocks without deliveries as well.
				timeblock = 'timeblock{}'.format(i)
				if str(i) in item['timeblocks']:
					postcode[timeblock] = item['timeblocks'][str(i)]
				else:
					postcode[timeblock] = 'ingen levering'

			# INSERT VALUES format
			tup = (
				postcode['code'],
				postcode['timeblock1'],
				postcode['timeblock2'],
				postcode['timeblock3'])
			# legg til i lista
			postcode_list.append(tup)
		return postcode_list

	def update_db(self, companyID=None, postcodes=None):
		""" Empty table and insert new values

			if companyid - get and format data.
			if postcodes - update db.
		"""

		if companyID:
			postcodes = self.get(companyID)
			postcodes = self.reformat(postcodes)
		elif postcodes:
			pass
		else:
			logger.error('update_db takes either companyID or postcodes')

		insert_str = "INSERT INTO dbo.Helper_Adams_Postnr VALUES(%d, %s, %s, %s)"

		with pymssql.connect(
				config.DB_HOST, config.DB_USERNAME, config.DB_PASSWORD, config.DB_DATABASE
				) as conn:
				with conn.cursor() as cursor:

					# empty table
					cursor.execute("DELETE FROM dbo.Helper_Adams_Postnr")
					conn.commit()

					# insert new values
					t0_exm = time.time()
					cursor.executemany(insert_str, postcodes)
					t1_exm = time.time()
					print('time exmany: ', t1_exm-t0_exm)

					# commit insertions
					t0_com = time.time()
					conn.commit()
					t1_com = time.time()
					print('time commit: ', t1_com-t0_com)

	def update_files(self, companyID=None, postcodes=None):

		if companyID:
			postcodes = self.get(companyID)
			postcodes = self.reformat(postcodes)
		elif postcodes:
			pass
		else:
			logger.error('update_db takes either companyID or postcodes')

		now = dt.date.today().isoformat()

		postcodes = self.get(CompanyID.ADAMS)
		raw_file_path = f'raw-{now}.json'
		with open(raw_file_path, 'w') as target:
			json.dump(postcodes, target, indent=2)
		logger.debug('saved raw to file')
		self.raw_file_path = raw_file_path

		formatted_postcodes = self.reformat(postcodes)
		formatted_file_path = f'formatted-{now}.json'
		with open(formatted_file_path, 'w') as target:
			json.dump(formatted_postcodes, target, indent=2)
		logger.debug('saved formatted to file')
		self.formatted_file_path = formatted_file_path

	def update_all(self, companyID=None, postcodes=None):
		""" Get new data and save to files and db """
		logger.debug('update all')
		if companyID:
			postcodes = self.get(companyID)
			postcodes = self.reformat(postcodes)
		elif postcodes:
			pass
		else:
			logger.error('update_db takes either companyID or postcodes')

		self.update_files(postcodes)
		self.update_db(postcodes)
