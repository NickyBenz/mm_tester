import pandas as pd


class Record:
    def __init__(self, counter, timestamp, series):
        self.counter = counter
        self.timestamp = timestamp
        self.series = series
    
    
    def get_instrument_data(self, instrument, key):
        lookup = instrument.name + "_" + key
        return self.series[lookup]
    
    
    def get(self, key):
        return self.series[key]
    
    
    def get_all(self):
        return self.series
    
