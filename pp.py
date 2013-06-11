# pretty print files with one json/line (e.g. tweet files)
import json
import sys
for line in sys.stdin:
  try:
    a=json.loads(line)
    print json.dumps(a,indent=4,sort_keys=True)
  except:
    a=0
