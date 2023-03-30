from typing import List
from pandas import pd
from . import record


class Data:
    def __init__(self, df: pd.DataFrame, frequency_milliseconds: int):
        self.df = df
        self.frequency = frequency_milliseconds
        cols = self.get_columns()
        
        self.features: List(str) = []
        self.instr_names: List(str) = []
        
        for col in cols:
            if "feat_" in col:
                self.features.append(col)
            elif '_mid' in col:
                names = col.split('_')
                self.instr_names.append(names[0])
        
        for name in self.instr_names:
            assert(name + "_bid" in cols)
            assert(name + "_ask" in cols)
    
    
    def get_feature_names(self)->List(str):
        return self.features
    
    
    def get_instrument_names(self)->List(str):
        return self.instr_names
    
        
    def get_columns(self)-> List(str):
        return list(self.df.columns)
    
    
    def get_rows(self) -> int:
        return self.df.shape[0]
    
    
    def get_record(self, time_counter, fetch_counter: int) -> record.Record:
        return record.Record(fetch_counter, self.get_index(time_counter), self.df.iloc[fetch_counter, :])
    
    
    def get_index(self, counter: int) -> pd.DatetimeIndex:
        return self.df.index[counter]
    
    
    def get_feature_history(self, counter: int, history: int) -> pd.DataFrame:
        idx = self.df.index[counter-history+1:counter+1]
        return self.df.loc[idx, self.features]
    
    
    def get_raw(self) -> pd.DataFrame:
        return self.df