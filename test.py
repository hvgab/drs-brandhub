import brandhub
import logging
import pprint
import os

pp = pprint.PrettyPrinter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_env_values_set():
	assert os.getenv('DB_HOST') is not None
	assert os.getenv('DB_USERNAME') is not None
	assert os.getenv('DB_PASSWORD') is not None
	assert os.getenv('DB_DATABASE') is not None

	assert os.getenv('BRANDHUB_POSTALCODES_URL') is not None
	assert os.getenv('BRANDHUB_COMPANYID_ADAMS') is not None
	assert os.getenv('BRANDHUB_COMPANYID_GODTLEVERT') is not None


def test_response_format():
	bh = brandhub.Brandhub_Postcodes()
	response = bh.get(brandhub.CompanyID.ADAMS)
	assert 'postalcodes' in response
	assert 'code' in response['postalcodes'][0]
	assert 'timeblocks' in response['postalcodes'][0]
	assert isinstance(response['postalcodes'][0]['code'], int)

	# Det skal ikke være andre alternativ enn 1,2,3 som key i timeblock keys.
	for key in response['postalcodes'][0]['timeblocks']:
		assert key in ('1','2','3')


def can_connect_to_server():
	try:
		with pymssql.connect(
			config.DB_HOST,
			config.DB_USERNAME,
			config.DB_PASSWORD,
			config.DB_DATABASE,
			timeout=10,
			login_timeout=5
				) as conn:
			with conn.cursor() as cursor:
				cursor.execute("SELECT @@VERSION")
				print(cursor.fetchone()[0])
				return True
	except Exception as e:
		logger.error('Is your IP whitelisted on the server?')
		return False


def test_can_connect_to_server():
	assert can_connect_to_server()


def save_to_file():
	import json
	bh = brandhub.Brandhub_Postcodes()
	r = bh.get(brandhub.CompanyID.ADAMS)
	with open('postalcodes.json', 'w') as out:
		json.dump(r, out, indent=4)

def test_search_file():
	bh = brandhub.Postcodes()
	search_results = bh.search_file('0139')
	print(search_results)
	return search_results


if __name__ == '__main__':
	# save_to_file()
	test_env_values_set()
	test_response_format()
	test_can_connect_to_server()
	test_search_file()
