""""
Creates the station collection in the database from the facility.dat file. Existing collection will be dropped.
"""

from pymongo import MongoClient
import string
import re
import argparse
import ast
from aka_call_sign import get_aka_sign

try:
    import mongodata
    print "mongodata found"
except ImportError:
    print "Can't find mongodataa"
    

class Facility(object):
    def __init__(self, data):
        self.fields = data.split('|')
        self.city=str.title(self.fields[0])
        self.state=self.fields[1]
        self.callsign=self.fields[5]
        self.displaysign=self.callsign
        self.channel=self.fields[6]
        self.country=self.fields[8]
        self.frequency=self.fields[9]
        self.service=self.fields[10]
        self.facility_type = self.fields[13]
        self.facility=self.fields[14]
        self.insert_template = string.Template('{"facility-id": "$fac", ' + \
                           '"fcc-call-sign": "$csign", ' + \
                           '"aka-call-sign": "$asign", ' + \
                           '"display-sign":"$dsign",' + \
                           '"freq": $freq, ' + \
                           '"amfm": "$amfm", ' + \
                           '"antennas": [], ' + \
                           '"address": {"city": "$city", "state": "$st", "country": "$ctr"}, ' + \
                           '}')
        
    def to_display_sign(self):
        '''
        Create the display sign. Some stations use a different call sign than the official one, just a few.
        '''
        call_sign = get_aka_sign(self.callsign)
        
        if self.service == "FM" and call_sign[-3:] != "-FM":
            call_sign = call_sign + "-FM"
         
        return call_sign
    
    def to_aka_sign(self):
        call_sign = get_aka_sign(self.callsign)

        if self.service == "FM" and call_sign[-3:] != "-FM":
            call_sign = call_sign + "-FM"
            
        return call_sign
        
    def to_insert_string(self):
        return self.insert_template.substitute(fac=self.facility, csign=self.callsign, asign=self.to_aka_sign(), dsign=self.to_display_sign(), freq=float(self.frequency),
                                               amfm=self.service, city=self.city, st=self.state, ctr=self.country)
    def to_dict(self):
        return ast.literal_eval(self.to_insert_string())
    
def get_facilities(facility_file):       
    checkCallSign = re.compile(r"(?:[C,K,W][A-Z]{2,3})(?:-AM/FM|-AM|-FM)?")
    checkTranslator_Repeater = re.compile(r"(?:[K,W][0-9]{3}[A-Z]{2})?")
    checkCallSignSvc = re.compile(r"(AM|FM)$")
#     checkFacType = re.compile(r"(AM|FT|FTB|H)")
    
    with open(facility_file, 'r') as fac:
        
        for fac_data in fac:
            
            facility = Facility(fac_data)
            
            # ignore stations with incomplete info
            if not facility.frequency.strip() or not facility.callsign.strip():
                continue
            
            if facility.facility_type == None:
                continue
            
            # if facility type is None, we should have a basic AM station.
            call_sign_match = checkCallSign.match(facility.callsign)
            if not call_sign_match:
                #TODO check for repeater stations
                continue
            
            if not checkCallSignSvc.match(facility.service):
                continue
            
            yield facility.to_dict()
    
        
def main(argv=None):
        
    argparser = argparse.ArgumentParser(description="Create station collection from fcc facility data")
    argparser.add_argument('--mongouri', dest='mongouri', default='mongodb://localhost:27017', required=False, help='mongodb connection string')
    argparser.add_argument('--facility_file', dest='facility_file', default='facility.dat', help="path to facility file (i.e. facility.dat) defaults to facility.dat in current directory")
    argparser.add_argument('--collection', dest='collection', default='stations', help='name of collection to create, default is stations. Drops existing collection if it exists')
    argparser.add_argument('--db_name', dest='dbname', required=True, help='name of mongodb database, required')
    args = argparser.parse_args()
    
    # assumes the database server is listening @ localhost:27017
    print 'mongouri: ', args.mongouri
    client = MongoClient(args.mongouri)
    print client
    db = client[args.dbname]
#     db.drop_collection(args.collection)
#     stations = db.create_collection(args.collection)
    stations = db.stations
    
    stations.insert(get_facilities(args.facility_file))
    stations.create_index("facility-id")
    
    # remove dups based on facility-id
    cursor = stations.aggregate([
        { '$group': {
            '_id': {'facility-id': '$facility-id'}, 'uniqueIds': {'$addToSet':"$facility-id"}, 'count':{'$sum': 1} } },
            {'$match': { 'count': {'$gt': 1} }}
    ])
    
    response = []
    for doc in cursor:
        del doc['facility_id'][0]
        for id in doc['facility_id']:
            response.append(id)
        
    if len(response) > 0:    
        stations.remove({'facility-id':{'$in': 'response'}})
    
    stations.create_index("fcc-call-sign")
    stations.create_index("aka-call-sign")
    
    print str(stations.count()) + " stations inserted"

if __name__ == "__main__":
    main()
    
