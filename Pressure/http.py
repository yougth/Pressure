import httplib
import urllib



httpClient = None
try:
    params = urllib.urlencode({'name': 'tom', 'age': 22})
    headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}
    httpClient = httplib.HTTPConnection("www.baidu.com", 80,timeout=30)
    httpClient.request("POST", "", "", headers)
    response = httpClient.getresponse()
    print response.status
    print response.reason
    print response.read()
    print response.getheaders()

except Exception, e:
    print e
finally:
    if httpClient:
        httpClient.close()

