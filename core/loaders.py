import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data"

def load_table(filename: str) -> pd.DataFrame:
    path = DATA_PATH / filename
    return pd.read_csv(path)