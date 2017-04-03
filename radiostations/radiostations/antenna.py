from abc import ABCMeta, abstractmethod

class Antenna(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, data):
        self.is_valid = False
        self.fac_id = None
        self.lat    = None      
        self.lat_dir = None  
        self.lat_mn = None
        self.lat_sc = None
        self.lon = None
        self.lon_dir = None
        self.lon_mn = None
        self.lon_sc = None
        
        self.is_valid = self.set_fields(data)
               
    @abstractmethod    
    def set_fields(self, data):
        return False
        
    def get_lat(self):  
        if not self.is_valid or self.lat == 0:
            return None     
        
        return self.lat + (self.lat_mn / 60) + (self.lat_sc / 3600)
    
    def get_long(self):    
        if not self.is_valid or self.lon == 0 or not self.lon_dir == "W":
            return None
        
        return (self.lon + (self.lon_mn / 60) + (self.lon_sc / 3600)) * - 1 
    
    def get_location(self):
        lat = self.get_lat()
        lon = self.get_long()
        
        if lat == None or lon == None:
            return None
        
        return  {"type": "Point", "coordinates": [ lon, lat ] }
    
    def get_tuple(self):
        return (self.appl_id, self.get_location())  