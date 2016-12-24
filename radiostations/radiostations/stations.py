""""
Creates the station collection in the database from the facility.dat file. Existing collection will be dropped.
"""

from pymongo import MongoClient
import string
import re
import argparse
import ast

class Facility(object):
    def __init__(self, data):
        self.fields = data.split('|')
        self.city=self.fields[0]
        self.state=self.fields[1]
        self.callsign=self.fields[5]
        self.channel=self.fields[6]
        self.frequency=self.fields[9]
        self.service=self.fields[10]
        self.facility=self.fields[14]
        self.insert_template = string.Template('{"facility-id": "$fac", ' + \
                           '"call-sign": "$csign", ' + \
                           '"freq": "$freq", ' + \
                           '"amfm": "$amfm", ' + \
                           '"antennas": [], ' + \
                           '"address": {"city": "$city", "state": "$st"}, ' + \
                           '}')
        
    def to_insert_string(self):
        return self.insert_template.substitute(fac=self.facility, csign=self.callsign, freq=self.frequency,
                                               amfm=self.service, city=self.city, st=self.state)
    def to_dict(self):
        return ast.literal_eval(self.to_insert_string())
    
def get_facilities(facility_file):       
    checkCallSign = re.compile(r"[K,W][A-Z]{2,3}")
    checkCallSignSvc = re.compile(r"(AM|FM)$")
    with open(facility_file, 'r') as fac:
        
        for fac_data in fac:
            facility = Facility(fac_data)
            
            if not checkCallSign.match(facility.callsign):
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
    
