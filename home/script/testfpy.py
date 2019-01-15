from jeputils import *

def testf(arr1):
    ret = call_jep("testf.py", "testfun", to_npa(arr1))
    return ret.data
