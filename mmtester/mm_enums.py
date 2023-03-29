from enum import Enum

class Side(Enum):
    BUY=1
    SELL=2
    
    
class Instrument(Enum):
    PERP_SWAP = 1
    INVERSE_FUTURE = 2
    

class FillType(Enum):
    MAKER = 1
    TAKER = 2
    
    
class OrderState(Enum):
    NEW = 1
    CANCELED = 2
    FILLED = 3
    