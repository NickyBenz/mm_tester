from pandas import pd
from . import record


class Data:
    def __init__(self, df: pd.DataFrame, frequency_milliseconds: int):
        self.df = df
        self.frequency = frequency_milliseconds
        
        
    def get_columns(self) -> list:
        return list(self.df.columns)
    
    
    def get_rows(self) -> int:
        return self.df.shape[0]
    
    
    def get_record(self, counter: int) -> record.Record:
        return record.Record(counter, self.get_index(counter), self.df.iloc[counter, :])
    
    
    def get_index(self, counter: int) -> pd.DatetimeIndex:
        return self.df.index[counter]
    
    
    def get_history(self, counter: int, history: int) -> pd.DataFrame:
        return self.df.iloc[counter-history+1:counter+1, :]
    
    
    def get_raw(self) -> pd.DataFrame:
        return self.df