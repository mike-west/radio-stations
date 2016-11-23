"""
Filters the FCC fm_eng_dat.dat
Uses FCC fm_eng_dat.dat file to update the stations collection. The station collection must be populated first
"""
from pymongo import MongoClient
import argparse
from radiostations.antenna import Antenna

class FMAntenna(Antenna):
           
    def set_fields(self, data):
        self.fields = data.split('|')
        
        try:
            self.fac_id = self.fields[20]
            self.lat = float(self.fields[30])      # latitude degrees
            self.lat_dir = self.fields[31]  # N or S but always N for US
            self.lat_mn = float(self.fields[32])  # latitude minutes
            self.lat_sc = float(self.fields[33])  # latitude seconds
            self.lon = float(self.fields[34])     # longitude degrees
            self.lon_dir = self.fields[35] # E or W but always W for US
            self.lon_mn = float(self.fields[36])  # longitude minutes
            self.lon_sc = float(self.fields[37])  # longitude seconds
        except ValueError:
            return False
        
        return True
    
def main(argv=None):
    collection_name = 'stations'
        
    argparser = argparse.ArgumentParser(description="Update station collection from am_ant_sys and am_eng_data data")
    argparser.add_argument('--eng_file', dest='eng_file', default='fm_eng_data.dat')
    argparser.add_argument('--db_name', dest='dbname', required=True)
    args = argparser.parse_args() 
    
    # assumes the database server is listening @ localhost:27017
    client = MongoClient()
    db = client[args.dbname]
    stations = db[collection_name]
    
    with open(args.eng_file, 'r') as eng_file:
        prev_location={}
        cnt = 0
        for eng in eng_file:
            cnt = cnt + 1
            print 'Reading record # ' + str(cnt)
            fm_antenna = FMAntenna(eng)
            
            if not fm_antenna.is_valid:
                continue
            
            facility_id = fm_antenna.fac_id
            location = fm_antenna.get_location()
            
            if facility_id == None or location == None:
                continue
            
            if len(prev_location) > 0 and location == prev_location:
                continue
            
            prev_location = location
            # TODO Update process is very slow, find alternative
            stations.find_one_and_update({'facility-id':facility_id}, {'$push':{'antennas':location}})
            
#             print 'facility-id ' + facility_id + ' updated with ' + str(location)

if __name__ == "__main__":
    main()