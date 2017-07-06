'''
Created on Jan 31, 2017

@author: mwest

Some radio stations display, or are known by, call signs other than the ones assigned by the FCC. The dictionary and
function below exchange official FCC call signs for the ones the stations is better know by. This can occur for several reasons but
often a station is an AM or FM repeater or translator for a parent station or it could be a branding decision by the owners.
'''

aka_call_signs = {
    'WBRK': 'WFAN'
    , 'KZZQ': 'KZNS'
    , 'W237CW-FX': 'WDAE-FM'
    , 'KSPN': 'ESPNLA'
    , 'K238BF': 'KPYN-FM'
    , 'K265DV': 'KTON-FM'
    , 'KIRO': 'ESPN Seattle'
    , 'K271AH': 'KAPS-FM'
    , 'WFAN': 'The FAN'
    , 'WFAN-FM': 'The FAN FM'
    , 'WIII': 'I-100'
    , 'W262AD': 'I-100'
    , 'WBGG': 'ESPN Pittsburgh'
    , 'W287CP': 'WYTS-FM'
    , 'WBIZ': 'The Brew'
    , 'WBIZ-FM': 'Z-100'
    , 'KKUU-FM': 'ESPN FM'
    }

def get_aka_sign(call_sign):
    if call_sign in aka_call_signs:
        return aka_call_signs[call_sign]
    else:
        return call_sign
