import oauth2
import sys

CONSUMER_KEY='J2IwwWhgHhLrpvBLZnbULA'
CONSUMER_SECRET='wrJkpf6e1IaKDk54JVrskNbdB09cRLxSVjjyCii8'
ACCESS_TOKEN='45123871-j5XGbr13L18qDdvNbALSJpZoWuuk3ke5fZe7ViZ4U'
ACCESS_SECRET='yRtocSTtQzh1emMvZYbJ4K6UpFU1dXFmfXUPmc68'

def request(url,http_method="GET",post_body=None,http_headers=None):
  consumer=oauth2.Consumer(key=CONSUMER_KEY,secret=CONSUMER_SECRET)
  token=oauth2.Token(key=ACCESS_TOKEN,secret=ACCESS_SECRET)
  client=oauth2.Client(consumer,token)    
  resp,content=client.request(url,method="GET",body=None,headers=None,force_auth_header=True)
  return content

print request(sys.argv[1])
