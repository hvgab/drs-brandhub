
import hug
import brandhub

po = brandhub.Postcodes()

@hug.post('/search')
def search(body):
	return po.search_file(body['postcode'])
