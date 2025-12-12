import pandas as pd
import json
from collections import defaultdict

# URL = https://www.kaggle.com/datasets/boltcutters/food-allergens-and-allergies

df = pd.read_csv("data/FoodData.csv")


df["Food"] = df["Food"].str.lower().str.strip()
df["Allergy"] = df["Allergy"].str.strip()


allergens_dict = (
    df.groupby("Allergy")["Food"]
      .apply(list)
      .to_dict()
)


with open("data/allergens_dict.json", "w", encoding="utf-8") as f:
    json.dump(allergens_dict, f, ensure_ascii=False, indent=4)

