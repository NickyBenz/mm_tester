import numpy as np
import os
import pandas as pd
from tqdm import tqdm


def generate_snapshot(input_path, output_path):
    chunksize = 1000 * 1000

    if os.path.exists(output_path):
        os.remove(output_path)

    for chunk in pd.read_csv(input_path, 
                              header=0,
                              chunksize=chunksize):
        chunk['date'] = pd.to_datetime(chunk['timestamp'], unit='us')
        chunk['td'] = pd.to_timedelta( chunk['timestamp'],'us')
        chunk = chunk.set_index('td')
        chunk = chunk.resample('150ms').last()
        chunk = chunk.reset_index(drop=True)
        chunk = chunk.set_index('date')
        chunk = chunk.drop(['exchange', 'timestamp', 'local_timestamp'], axis=1)
        chunk.dropna().to_csv(output_path, mode='a', header=not os.path.exists(output_path))
        

def bid_ask_imbalance(bid_volumes, ask_volumes, level):
    total_bid_volume = sum(bid_volumes[:level])
    total_ask_volume = sum(ask_volumes[:level])
    
    imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
    return ("bid_ask_imbalance_{i}".format(i=level), imbalance)


def weighted_imbalance(bid_prices, bid_volumes, ask_prices, ask_volumes, depth):
    best_bid = bid_prices[0]
    best_ask = ask_prices[0]

    weighted_bid_volume = 0
    weighted_ask_volume = 0
    
    for i in range(0, depth):
        weighted_bid_volume += (best_ask - bid_prices[i]) / (best_ask - best_bid) * bid_volumes[i]
        weighted_ask_volume += (ask_prices[i] - best_bid) / (best_ask - best_bid) * ask_volumes[i] 
    
    imbalance = (weighted_bid_volume - weighted_ask_volume) / (weighted_bid_volume + weighted_ask_volume)
    return ("weighted_imbalance_{i}".format(i=depth), imbalance)


def orderbook_slope(bid_prices, bid_volumes, ask_prices, ask_volumes, depth):
    bid_prices = np.array(bid_prices, dtype=np.float64)
    bid_volumes = np.array(bid_volumes, dtype=np.float64)
    ask_prices = np.array(ask_prices, dtype=np.float64)
    ask_volumes = np.array(ask_volumes, dtype=np.float64)

    bid_volumes = np.cumsum(bid_volumes[:depth])
    bid_prices = bid_prices[:depth]

    ask_volumes = np.cumsum(ask_volumes[:depth])
    ask_prices = ask_prices[:depth]

    prices = np.concatenate((bid_prices, ask_prices))
    volumes = np.concatenate((bid_volumes, ask_volumes))

    A = np.vstack([prices, np.ones_like(prices)]).T
    slope, _ = np.linalg.lstsq(A, volumes, rcond=None)[0]
    return ("ob_slope_{i}".format(i=depth), slope)        


def depth_weighted_spread(bid_prices, bid_volumes, ask_prices, ask_volumes, depth):
    weighted_spreads_sum = 0
    total_volume = 0
    
    for i in range(depth):
        spread = ask_prices[i] - bid_prices[i]
        avg_volume = (bid_volumes[i] + ask_volumes[i]) / 2.0
        
        weighted_spreads_sum += spread * avg_volume
        total_volume += avg_volume
    
    depth_weighted_spread = weighted_spreads_sum / total_volume
    return ("depth_spread_{i}".format(i=depth), depth_weighted_spread)


def ewma(data, window):
    alpha = 2 /(window + 1.0)
    alpha_rev = 1-alpha
    n = data.shape[0]
    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = data[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = data*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    return out


def generate_prices(filename, name):
    book = pd.read_csv(filename, header=0, index_col=['date'], parse_dates=['date'])
    prices_df = pd.DataFrame(index=book.index)
    
    for i in tqdm(range(0, book.shape[0])):
        curr_index = book.index[i]
        row = book.iloc[i, :]
        bid_price = row['bids[0].price']
        ask_price = row['asks[0].price']
        prices_df.loc[curr_index, name + "_bid"] = bid_price
        prices_df.loc[curr_index, name + "_ask"] = ask_price
        prices_df.loc[curr_index, name + "_mid"] = (bid_price + ask_price) * 0.5
    return prices_df

def generate_features(filename, name):
    book = pd.read_csv(filename, header=0, index_col=['date'], parse_dates=['date'])
    bid_price_cols = []
    ask_price_cols = []
    bid_amount_cols = []
    ask_amount_cols = []

    features_df = pd.DataFrame(index=book.index)

    for i in range(0, 24):
        bid_price_cols.append('bids[{i}].price'.format(i=i))
        ask_price_cols.append('asks[{i}].price'.format(i=i))
        bid_amount_cols.append('bids[{i}].amount'.format(i=i))
        ask_amount_cols.append('asks[{i}].amount'.format(i=i))


    for i in tqdm(range(0, book.shape[0])):
        curr_index = book.index[i]
        row = book.iloc[i, :]
        bid_prices = row[bid_price_cols].values
        ask_prices = row[ask_price_cols].values
        bid_volumes = row[bid_amount_cols].values
        ask_volumes = row[ask_amount_cols].values
        mid_price = (bid_prices[0] + ask_prices[0]) / 2.0
        features_df.loc[curr_index, name + "_mid"] = mid_price
        features_df.loc[curr_index, name + "_bid"] = bid_prices[0]
        features_df.loc[curr_index, name + "_ask"] = ask_prices[0]
        features_df.loc[curr_index, "spread"] = (ask_prices[0] - bid_prices[0])
            
        kv = bid_ask_imbalance(bid_volumes, ask_volumes, 1)
        
        for level in [3, 5, 8, 12]:
            kv = bid_ask_imbalance(bid_volumes, ask_volumes, level)
            features_df.loc[curr_index, kv[0]] = kv[1]
            kv = weighted_imbalance(bid_prices, bid_volumes, ask_prices, ask_volumes, level)
            features_df.loc[curr_index, kv[0]] = kv[1]
            kv = orderbook_slope(bid_prices, bid_volumes, ask_prices, ask_volumes, level)
            features_df.loc[curr_index, kv[0]] = kv[1]
            kv = depth_weighted_spread(bid_prices, bid_volumes, ask_prices, ask_volumes, level)
            features_df.loc[curr_index, kv[0]] = kv[1]
        
        for history in [300, 600, 1200]:
            if i >= history:
                hist_idx = book.index[i-history:i+1]
                mid_prices = np.asarray(features_df.loc[hist_idx, name + "_mid"].values, dtype=np.float64)
                spreads = np.asarray(features_df.loc[hist_idx, "spread"].values, dtype=np.float64)
                
                features_df.loc[curr_index, "feat_mdma_{i}".format(i=history)] = np.mean(mid_prices)
                features_df.loc[curr_index, "feat_mdema_{i}".format(i=history)] = ewma(mid_prices, history)[-1]
                features_df.loc[curr_index, "feat_mdvol_{i}".format(i=history)] = np.std(mid_prices)

                features_df.loc[curr_index, "feat_spma_{i}".format(i=history)] = np.mean(spreads)
                features_df.loc[curr_index, "feat_spema_{i}".format(i=history)] = ewma(spreads, history)[-1]
                features_df.loc[curr_index, "feat_spvol_{i}".format(i=history)] = np.std(spreads)
    
    return features_df
    

def align_dataframes(primary_df, price_df):
    df = pd.concat([primary_df, price_df], axis=1, join="outer")
    cols = list(price_df.columns)
    df.loc[:, cols] = df.loc[:, cols].ffill()
    df.dropna(inplace = True)
    return df

import sys

if __name__ == "__main__":
    perpfile = sys.argv[1]
    futurefile = sys.argv[2]
    
    generate_snapshot(perpfile, "perp_book.csv")
    generate_snapshot(futurefile, "future_book.csv")
    perp_feat_df = generate_features("perp_book.csv", "perp")
    fut_price_df = generate_prices("future_book.csv", "future")
    df = align_dataframes(perp_feat_df, fut_price_df)
    df.to_csv("data.csv", header=0)
    
    
    
