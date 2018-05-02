import brandhub
import time
import config
import pprint

pp = pprint.PrettyPrinter()

t0_main = time.time()

bh = brandhub.Postcodes()
search_results = bh.search_file('0139')
print(search_results)
