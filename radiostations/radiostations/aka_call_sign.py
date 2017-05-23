'''
Created on Jan 31, 2017

@author: mwest

Some radio stations display, or are known by, call signs other than the ones assigned by the FCC. The dictionary and
function below exchange official FCC call signs for the ones the stations is better know by. This can occur for several reason but
often a station is an AM or FM repeater or translator for a parent station or it could be a branding issue by the owners.
'''

aka_call_signs = {
    'WBRK': 'WFAN'
    , 'KZZQ': 'KZNS'
    , 'W237CW-FX': 'WDAE-FM'
    , 'KSPN': 'ESPNLA'
    }

def get_aka_sign(call_sign):
    if call_sign in aka_call_signs:
        return aka_call_signs[call_sign]
    else:
        return call_sign
