import hmac
import httplib2
import socket
import re

from base64 import b64encode
from hashlib import sha256
from lxml import objectify
from time import strftime, gmtime
from urllib import quote

AMAZON_RE = re.compile('http://www.amazon.+?/(?P<ASIN>[a-zA-Z0-9]{10,11})/.+?')
def asin_from_url(url):
    match = AMAZON_RE.match(url)
    if match:
        return match.groupdict()['ASIN']

class AmazonAPI(object):
    version = '2009-10-01'
    host = 'ecs.amazonaws.com'
    path = '/onca/xml'
    
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        
    def build_url(self, **kwargs):
        # mostly from basti's python-amazon-product-api:
        # http://bitbucket.org/basti/python-amazon-product-api/src/tip/amazonproduct.py#cl-321
        if 'AWSAccessKeyId' not in kwargs:
            kwargs['AWSAccessKeyId'] = self.access_key
            
        if 'Service' not in kwargs:
            kwargs['Service'] = 'AWSECommerceService'
            
        if 'version' not in kwargs:
            kwargs['version'] = self.version
            
        kwargs['Timestamp'] = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
        
        # create signature
        keys = sorted(kwargs.keys())
        args = '&'.join('%s=%s' % (key, quote(str(kwargs[key]))) 
                        for key in keys)
        
        msg = 'GET\n%s\n%s\n%s' % (self.host, self.path, args.encode('utf-8'))
        signature = quote(b64encode(hmac.new(self.secret_key, msg, sha256).digest()))
        
        url = 'http://%s%s?%s&Signature=%s' % (self.host, self.path, args, signature)
        return url
    
    def raw_api_call(self, url, max_timeout=4):
        sock = httplib2.Http(timeout=max_timeout)
        
        request_headers = {'User-Agent': 'Python-httplib2'}
        
        try:
            headers, response = sock.request(url)
        except socket.timeout:
            raise ValueError('Socket timed out')
                
        status = int(headers.pop('status', 200))
        if status != 200:
            raise ValueError('Returned status: %s' % (status))
        
        return objectify.fromstring(response)
    
    def item_search(self, search_index, **params):
        url = self.build_url(Operation='ItemSearch', SearchIndex=search_index, **params)
        data = self.raw_api_call(url)
        return [self.resource_dict(node) for node in data.Items.Item]
    
    def item_lookup(self, item_id, **params):
        url = self.build_url(
            Operation='ItemLookup',
            ItemId=item_id, 
            ResponseGroup='ItemAttributes,Images', # EditorialReview
            **params)
        data = self.raw_api_call(url)
        return self.resource_dict(data.Items.Item[0])
    
    def resource_dict(self, data):
        attributes = ['Author', 'Edition', 'ISBN', 'ListPrice', 'NumberOfPages',
            'ProductGroup', 'PublicationDate', 'Publisher', 'RunningTime',
            'Title']
        
        data_dict = {}
        data_dict['asin'] = data.ASIN
        
        for attr in attributes:
            data_dict[attr.lower()] = getattr(data.ItemAttributes, attr, '')
        
        try:
            data_dict['review'] = data.EditorialReviews.EditorialReview.Content
        except AttributeError:
            data_dict['review'] = ''
        
        data_dict['image'] = ''
        for img in ['SmallImage', 'MediumImage', 'LargeImage']:
            if getattr(data, img, None):
                data_dict['image'] = getattr(data, img).URL
        
        for k, v in data_dict.iteritems():
            if not isinstance(v, basestring):
                data_dict[k] = v.text
        
        if not re.match('%d{4}-%d{2}-%d{2}', data_dict['publicationdate']):
            data_dict['publicationdate'] = None
        
        return data_dict
