'''
Created on Jan 31, 2017

@author: Owner

Some radio stations display, or are known by, call signs other than the ones assigned by the FCC. The dictionary and
function below exchange official FCC call signs for the ones the stations is better know by.
'''

aka_call_signs = {
    'WBRK': 'WFAN'
    , 'KZZQ': 'KZNS'
    }

def get_aka_sign(call_sign):
    if call_sign in aka_call_signs:
        return aka_call_signs[call_sign]
    else:
        return call_sign
