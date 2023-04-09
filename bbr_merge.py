import json
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tqdm

def read_json_file(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return pd.json_normalize(data)[['unitId','evaluationInfos','bbrInfoBox.lotSize', 'bbrInfoBox.area', 'bbrInfoBox.evaluationPrice', 'unitInfo.toiletQuantity','unitInfo.bathroomQuantity','unitInfo.propertyUnitType','bfenr']]

def merge_bbr_func(path: str):
    data_dir = Path(path)
    json_files = list(data_dir.glob('*.json'))

    with ThreadPoolExecutor() as executor:
        dfs = list(tqdm.tqdm(executor.map(read_json_file, json_files)))

    full_df1 = pd.concat(dfs)
    return full_df1

# path = 'data/bbr'
# full_df = merge_bbr_func(path)
# full_df = full_df.reset_index(drop=True)

# full_df.to_parquet('data/bbr_merged.pq')