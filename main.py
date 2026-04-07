from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "FAF5.7.1_2018-2024" / "FAF5.7.1_2018-2024.csv"

df = pd.read_csv(csv_path, nrows=20)
print(df.head(5).T)

