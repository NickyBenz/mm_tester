from . import record


class Data:
    def __init__(self, df, frequency):
        self.df = df
        self.frequency = frequency
        
        
    def get_columns(self):
        return list(self.df.columns)
    
    
    def get_rows(self):
        return self.df.shape[0]
    
    
    def get_record(self, counter):
        return record.Record(counter, self.get_index(counter), self.df.iloc[counter, :])
    
    
    def get_index(self, counter):
        return self.df.index[counter]
    
    
    def get_history(self, counter, history):
        return self.df.iloc[counter-history:counter+1, :]
    
    
    def get_raw(self):
        return self.df