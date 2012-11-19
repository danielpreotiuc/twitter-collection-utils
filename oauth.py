import oauth2
import sys
import os

def loadTokensIndex(loc):
  f = file(loc,"r")
  index = []
  for line in f.readlines():
    if line.startswith("#"): continue
    parts = [x.strip() for x in line.split(",")]
    (consumer_key,consumer_secret,auth_key,auth_secret) = parts
    tokens = dict()
    tokens["CLIENT_KEY"] = consumer_key
    tokens["CLIENT_SECRET"] = consumer_secret
    tokens["ATOKEN_KEY"] = auth_key
    tokens["ATOKEN_SECRET"] = auth_secret
    index = index + [tokens]
  return index

def request(url,http_method="GET",post_body=None,http_headers=None):
  consumer=oauth2.Consumer(key=tokens["CLIENT_KEY"],secret=tokens["CLIENT_SECRET"])
  token=oauth2.Token(key=tokens["ATOKEN_KEY"],secret=tokens["ATOKEN_SECRET"])
  client=oauth2.Client(consumer,token)
  resp,content=client.request(url,method="GET",body=None,headers=None,force_auth_header=True)
  return content

CONF_DIR = os.getenv('HOME') # where to find the configuration
CONSUMER = (int(sys.argv[2]) if len(sys.argv) >= 3 else 0)
tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

print request(sys.argv[1])
