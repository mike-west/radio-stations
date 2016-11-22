"""
Uses FCC am_ant_sys file to update the stations collection. The stations collection must be populated first
Gets facility id and computes the latitude and longitude from the am_ant_sys file. Uses the facility_id from am_eng_data
to look up the information from the station. 
"""
from pymongo import MongoClient
import argparse
import sys
from radiostations.antennae import Antennae

class AMAntennae(Antennae):
    def set_fields(self, data):
        self.fields = data.split('|')
        
        try:
            self.appl_id    = self.fields[2]
            self.lat        = float(self.fields[12])    # latitude degrees
            self.lat_dir    = self.fields[13]           # N or S but always N for US
            self.lat_mn     = float(self.fields[14])    # latitude minutes
            self.lat_sc     = float(self.fields[15])    # latitude seconds
            self.lon        = float(self.fields[16])    # longitude degrees
            self.lon_dir    = self.fields[17]           # E or W but always W for US
            self.lon_mn     = float(self.fields[18])    # longitude minutes
            self.lon_sc     = float(self.fields[19])    # longitude seconds
        except ValueError:
            return False
        
        return True
   
        
def main(argv=None):
    collection_name = 'stations'
        
    argparser = argparse.ArgumentParser(description="Update station collection from am_ant_sys and am_eng_data data")
    argparser.add_argument('--ant_file', dest='ant_file', default='am_ant_sys.dat')
    argparser.add_argument('--eng_file', dest='eng_file', default='am_eng_data.dat')
    argparser.add_argument('--db_name', dest='dbname', required=True)
    args = argparser.parse_args()
   
    # create a hash table where the key is the application id and the value is the facility id 
    fac_ids = {}
    with open(args.eng_file, 'r') as eng_file:
        for eng in eng_file:
            fields = eng.split('|')
            
            if fac_ids.has_key(fields[1]) == False:
                fac_ids[fields[1]] = fields[4]
            else:
                sys.stderr.write("applId " + fields[1] + " is already present in fac_ids\n") 
                continue  
    
    # assumes the database server is listening @ localhost:27017
    client = MongoClient()
    db = client[args.dbname]
    stations = db[collection_name]
    
    with open(args.ant_file, 'r') as ant_file:
        prev_location = {}
        for ant in ant_file:
            am_antennae = AMAntennae(ant)
            
            if not am_antennae.is_valid:
                continue
            
            if not fac_ids.has_key(am_antennae.appl_id):
                sys.stderr.write('applId ' + am_antennae.appl_id + ' has no entry in fac_ids\n')
                continue
            
            if am_antennae.get_lat() == None or am_antennae.get_long() == None:
                continue
            facility_id = fac_ids[am_antennae.appl_id]
            location = am_antennae.get_location()
            
            if location == None:
                continue
            
            if len(prev_location) > 0 and location == prev_location:
                continue
            
            prev_location = location
            # TODO Update process is very slow, find alternative
            stations.find_one_and_update({'facility-id':facility_id}, {'$push':{'antennas':location}})
            

if __name__ == "__main__":
    main()