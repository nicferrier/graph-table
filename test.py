"""
Tests for databin
"""

import subprocess
def createdb(name):
    pin = subprocess.Popen(["createdb", name], subprocess.PIPE)
    pin.wait()
    if pin.returncode:
        raise Exception("db create failed")

def dropdb(name):
    pin = subprocess.Popen(["dropdb", name], subprocess.PIPE)
    pin.wait()
    if pin.returncode:
        raise Exception("db drop failed")
    
import unittest
import databin
import os
from StringIO import StringIO

DATA = """date,domain,count
2010-11-03 00:00:00+00,aim.com,82
2010-11-04 00:00:00+00,aim.com,14
2010-11-03 00:00:00+00,aol.com,2026
2010-11-04 00:00:00+00,aol.com,5237
2010-11-06 00:00:00+00,aol.co.uk,1
2010-11-03 00:00:00+00,att.net,17
2010-11-04 00:00:00+00,att.net,1
2010-11-06 00:00:00+00,bell.net,7
2010-11-05 00:00:00+00,bellsouth.net,6
2010-11-08 00:00:00+00,bellsouth.net,27
2010-11-04 00:00:00+00,btinternet.com,252
2010-11-05 00:00:00+00,btinternet.com,29
2010-11-17 00:00:00+00,fastmail.fm,7
2010-11-03 00:00:00+00,gmail.com,8458
2010-11-04 00:00:00+00,gmail.com,30728
2010-11-03 00:00:00+00,hotmail.ca,98
2010-11-04 00:00:00+00,hotmail.ca,5
2010-11-03 00:00:00+00,hotmail.com,52862
2010-11-04 00:00:00+00,hotmail.com,93010
2010-11-03 00:00:00+00,live.com,4099
2010-11-04 00:00:00+00,live.com,6546
"""

class DataBinTest(unittest.TestCase):
    def setUp(self):
        os.environ["DATABIN_DB"] = "testdatabin"
        createdb("testdatabin")

    def tearDown(self):
        dropdb("testdatabin")

    def test_upload(self):
        datafd = StringIO(DATA)
        databin.handle_args([
                "test", 
                "testdata", 
                "domain=text", 
                "date=timestamp with time zone",
                "count=integer"
                ], datafd)
        # Now get the data
        sd = StringIO()
        databin.get("testdata", sd)
        
        # Mangle the data a bit so we can assert it
        totest = "\n".join(sd.getvalue().split("\n")[:13])
        self.assert_(totest == """<table>
<tr>
<th id="id__id">id</th>
<th id="id__date">date</th>
<th id="id__count">count</th>
<th id="id__domain">domain</th>
</tr>
<tr>
<td header="id__id">1</td>
<td header="id__date">2010-11-03 00:00:00+00:00</td>
<td header="id__count">82</td>
<td header="id__domain">aim.com</td>
<tr>""", "%s is not correct" % totest)
                

if __name__ == "__main__":
    unittest.main()

# End
