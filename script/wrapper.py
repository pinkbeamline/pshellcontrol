from jeputils import *

def double_array(arr):
    ret = call_jep("test_jep", "double_array", to_npa(arr))
    return ret.data