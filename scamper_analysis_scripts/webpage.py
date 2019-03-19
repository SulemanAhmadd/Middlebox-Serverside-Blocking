import requests
import re

headers = {	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding':'identity,deflate;q=0.5,gzip;q=0.5',
			'Accept-Language':'en-US,en;q=0.5',
			'Connection':'close',
			'Upgrade-Insecure-Requests':'1',
			'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
	  	}

'''

2xx - Success
3xx - Redirection
4xx - Client Error
5xx - Server Error

'''
status_code_200 = re.compile(r'^HTTP\/[0-9]\.[0-9] [2]')
status_code_300 = re.compile(r'^HTTP\/[0-9]\.[0-9] [3]')
status_code_400 = re.compile(r'^HTTP\/[0-9]\.[0-9] [4]')
status_code_500 = re.compile(r'^HTTP\/[0-9]\.[0-9] [5]')

class Webpage(object):

	def __init__(self, webpage_path):
		self.status_code = ''
		self.webpage_complete = None
		self.dir_path = webpage_path
		self.external_crawl = False
		self.domain_name = self.dir_path.split('/')[-1].strip('.txt')

	def parse_webpage(self, webpage_dir):
		
		with open(webpage_dir, 'r') as file:
			page = file.readlines()
			page = ''.join(page)

			self.webpage_complete = True if '</html>' in page else False

			if status_code_200.match(page):
				self.status_code = '200'

			elif status_code_300.match(page):
				self.status_code = '300'

			elif status_code_400.match(page):
				self.status_code = '400'

			elif status_code_500.match(page):
				self.status_code = '500'

	def replace_corrupt_page(self):
		
		if not self.webpage_complete or self.status_code == '300':

			response = requests.get('https://' + self.domain_name, headers=headers)

			self.status_code = str(response.status_code)
			self.webpage_complete = True
			self.external_crawl = True

			with open(self.dir_path, 'w') as page_file:
				page_file.write(response.text.encode('utf-8'))

	def p_print(self):
		print ("*****************************************************************************")
		print ("Domain Name: %s" % self.domain_name)
		print ("Status Code: %s" % self.status_code)
		print ("Webpage Complete: %r" % self.webpage_complete)
		print ("External Crawler Used: %r" % self.external_crawl)
		print ("*****************************************************************************")

