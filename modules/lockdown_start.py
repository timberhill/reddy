import numpy as np
from datetime import datetime

# dates from https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdowns

def load_national_lockdown_list():
    # columns: Country,State,Start,End,Level
    data = np.genfromtxt("../data/lockdown_start.csv", delimiter=",", dtype=np.str).T
    national_mask = (data[4] == "National")

    return {
        "Country" : data[0][national_mask],
        "Start"   : [datetime.strptime(x.split("[")[0].strip(), "%Y-%m-%d") for x in data[2][national_mask]]
    }
