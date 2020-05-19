import pandas as pd
from datetime import datetime

# dates from https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdowns

def load_national_lockdown_list():
    data = pd.read_csv("modules/lockdown_start.csv", header=0, sep=",")
    data["Start"] = data.apply(lambda row: datetime.strptime(row["Start"].split("[")[0].strip(), "%Y-%m-%d"), axis=1)
    national_mask = (data["Level"] == "National")

    return data.where(national_mask).dropna(axis=0, how='any')
