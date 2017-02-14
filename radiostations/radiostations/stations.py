""""
Creates the station collection in the database from the facility.dat file. Existing collection will be dropped.
"""

from pymongo import MongoClient
import string
import re
import argparse
import ast
import aka_call_sign
from radiostations.aka_call_sign import get_aka_sign

class Facility(object):
    def __init__(self, data):
        self.fields = data.split('|')
        self.city=self.fields[0]
        self.state=self.fields[1]
        self.callsign=self.fields[5]
        self.displaysign=self.callsign
        self.channel=self.fields[6]
        self.frequency=self.fields[9]
        self.service=self.fields[10]
        self.facility=self.fields[14]
        self.insert_template = string.Template('{"facility-id": "$fac", ' + \
                           '"fcc-call-sign": "$csign", ' + \
                           '"aka-call-sign": "$asign", ' + \
                           '"display-sign":"$dsign",' + \
                           '"freq": $freq, ' + \
                           '"amfm": "$amfm", ' + \
                           '"antennas": [], ' + \
                           '"address": {"city": "$city", "state": "$st"}, ' + \
                           '}')
        
    def to_display_sign(self):
        '''
        Create the display sign. Some stations use a different call sign than the official one, just a few.
        '''
        call_sign = get_aka_sign(self.callsign)
        
        if self.service == "FM" and call_sign[-3:] != "-FM":
            call_sign = call_sign + "-FM"
            
        return call_sign + ' ' + '{:g}'.format(float(self.frequency))
    
    def to_aka_sign(self):
        call_sign = get_aka_sign(self.callsign)
        if self.service == "FM" and call_sign[-3:] != "-FM":
            call_sign = call_sign + "-FM"
            
        return call_sign
        
    def to_insert_string(self):
        return self.insert_template.substitute(fac=self.facility, csign=self.callsign, asign=self.to_aka_sign(), dsign=self.to_display_sign(), freq=float(self.frequency),
                                               amfm=self.service, city=self.city, st=self.state)
    def to_dict(self):
        return ast.literal_eval(self.to_insert_string())
    
def get_facilities(facility_file):       
    checkCallSign = re.compile(r"(?:[K,W][A-Z]{2,3})(?:-AM/FM|-AM|-FM)?")
    checkCallSignSvc = re.compile(r"(AM|FM)$")
    
    with open(facility_file, 'r') as fac:
        
        for fac_data in fac:
            
            facility = Facility(fac_data)
            
            call_sign_match = checkCallSign.match(facility.callsign)
            if not call_sign_match:
                continue;
            
            if not checkCallSignSvc.match(facility.service):
                continue
            
            yield facility.to_dict()
    
        
def main(argv=None):
        
    argparser = argparse.ArgumentParser(description="Create station collection from fcc facility data")
    argparser.add_argument('--facility_file', dest='facility_file', default='facility.dat', help="path to facility file (i.e. facility.dat) defaults to facility.dat in current directory")
    argparser.add_argument('--collection', dest='collection', default='stations', help='name of collection to create, default is stations. Drops existing collection if it exists')
    argparser.add_argument('--db_name', dest='dbname', required=True, help='name of mongodb database, required')
    args = argparser.parse_args()
    
    # assumes the database server is listening @ localhost:27017
    client = MongoClient()
    db = client[args.dbname]
    db.drop_collection(args.collection)
    stations = db.create_collection(args.collection)
    
    stations.insert(get_facilities(args.facility_file))
    stations.create_index("call-sign")
    stations.create_index("facility-id")
    
    print str(stations.count()) + " stations inserted"

if __name__ == "__main__":
    main()
    
