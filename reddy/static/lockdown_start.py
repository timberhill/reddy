import numpy as np
from datetime import datetime

# dates from https://en.wikipedia.org/wiki/COVID-19_pandemic_lockdowns


def national_lockdown_list():
    # columns: Country,State,Start,End,Level
    source_csv = os.path.join(os.path.dirname(__file__), "lockdown_start.csv")
    data = np.genfromtxt(source_csv, delimiter=",", dtype=np.str).T
    national_mask = (data[4] == "National")

    return {
        "Country": data[0][national_mask],
        "Start": [datetime.strptime(x.split("[")[0].strip(), "%Y-%m-%d") for x in data[2][national_mask]]
    }
