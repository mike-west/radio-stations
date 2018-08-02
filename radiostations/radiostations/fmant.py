"""
Filters the FCC fm_eng_dat.dat
Uses FCC fm_eng_dat.dat file to update the stations collection. The station collection must be populated first

Uses unordered_bulk_op() for inserts. My test indicates that the number of records per insert does not change
the total time required. Therefore I have set the count to update every 10,000 records. 
"""
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import argparse
from antenna import Antenna
import time

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
        
    argparser = argparse.ArgumentParser(description="Update station collection from fm_eng_data.dat")
    argparser.add_argument('--eng_file', dest='eng_file', default='fm_eng_data.dat')
    argparser.add_argument('--collection', dest='collection', default='stations', help='name of collection to create, default is stations')
    argparser.add_argument('--db_name', dest='dbname', required=True)
    args = argparser.parse_args() 
    
    # assumes the database server is listening @ localhost:27017 
    client = MongoClient()
    db = client[args.dbname]
    stations = db[args.collection]
    cnt = 0
    max_inserts = 10000
    inserts = stations.initialize_unordered_bulk_op()
    
    with open(args.eng_file, 'r') as eng_file:
        prev_location={}

        for eng in eng_file:               
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
            
            inserts.find({'facility-id':facility_id}).update({'$push':{'antennas':location}})
            cnt = cnt + 1
            if cnt == max_inserts:
                cnt = 0
                try:
                    print 'starting updates...'
                    start = time.time()
                    inserts.execute()
                    end = time.time()
                    print "Time to bulk update " + str(max_inserts) + " records " + str(end - start) + " secs"
                    inserts = stations.initialize_unordered_bulk_op()
                except BulkWriteError as bwe:
                    print bwe.details 
                    inserts = stations.initialize_unordered_bulk_op()
                     
             

        try:
            print 'starting updates...'
            start = time.time()
            inserts.execute()
            end = time.time()
            print "Time to bulk update " + str(cnt) + " records " + str(end - start) + " secs"
        except BulkWriteError as bwe:
            print bwe.details 
        print str(upd) + ' stations updated'
        
    print "Completed"

if __name__ == "__main__":
    main()
    