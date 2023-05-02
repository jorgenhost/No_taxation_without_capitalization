import json
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tqdm

# Reads JSON-file from API and normalizes/flattens data as arrays in JSON-file have different sizes.
def read_json_file(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return pd.json_normalize(data)[['unitId','evaluationInfos','bbrInfoBox.lotSize', 'bbrInfoBox.area', 'bbrInfoBox.evaluationPrice', 'unitInfo.toiletQuantity','unitInfo.bathroomQuantity','unitInfo.propertyUnitType','bfenr']]

# Auxiliary merge function for BBR data from api.boliga.dk
def merge_bbr_func(path: str):
    data_dir = Path(path)
    json_files = list(data_dir.glob('*.json'))

    with ThreadPoolExecutor() as executor:
        dfs = list(tqdm.tqdm(executor.map(read_json_file, json_files)))

    full_df1 = pd.concat(dfs)
    return full_df1

# Path of data directory defined in scraper notebook.
# Adjusts datatypes to conserve memory usage
# Saves to parquet to preserve data types.
path = 'data/bbr'
full_df = merge_bbr_func(path)
full_df = full_df.reset_index(drop=True)
full_df['unitInfo.propertyUnitType']=full_df['unitInfo.propertyUnitType'].astype('category')
full_df['unitInfo.bathroomQuantity']=full_df['unitInfo.bathroomQuantity'].astype('int8')
full_df['unitInfo.toiletQuantity']=full_df['unitInfo.toiletQuantity'].astype('int8')
full_df['bbrInfoBox.lotSize']=full_df['bbrInfoBox.lotSize'].astype('int32')
full_df['bbrInfoBox.area']=full_df['bbrInfoBox.area'].astype('int16')
full_df.to_parquet('data/bbr_merged.pq')