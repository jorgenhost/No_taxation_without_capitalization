import json
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tqdm

# Reads JSON-file from API and normalizes/flattens data as arrays in JSON-file have different sizes.
def read_pq_file(pq_file):
    data = pd.read_parquet(pq_file)
    return data[['unitId','evaluationInfos','bbrInfoBox.lotSize', 'bbrInfoBox.area', 'bbrInfoBox.evaluationPrice', 'unitInfo.toiletQuantity','unitInfo.bathroomQuantity','unitInfo.propertyUnitType','bfenr']]

# Auxiliary merge function for BBR data from api.boliga.dk
def merge_bbr_func(path: str):
    data_dir = Path(path)
    pq_files = list(data_dir.glob('*.pq'))

    with ThreadPoolExecutor() as executor:
        dfs = list(tqdm.tqdm(executor.map(read_pq_file, pq_files)))

    full_df1 = pd.concat(dfs)
    return full_df1

# Path of data directory defined in scraper notebook.
# Saves to parquet to preserve data types.
path = 'data/bbr'
full_df = merge_bbr_func(path)
full_df = full_df.reset_index(drop=True)
full_df.to_parquet('data/bbr_merged.pq')