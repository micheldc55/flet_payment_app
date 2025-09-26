import argparse

import json

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, default=0)
args = parser.parse_args()

idx = args.idx

df = pd.read_csv("src/payments_src/db/csv_db/tables/loan.csv")

df["payment_list"] = df["payment_list"].apply(lambda x: json.loads(x))

if idx >= len(df):
    print("Index is out of range! Pass a valid index as an argument.")
    exit()

print(df.iloc[idx]["payment_list"])