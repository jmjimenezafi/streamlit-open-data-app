# flake8: noqa
# ruff: noqa
# pylint: skip-file

import pandas as pd
import re
import ast

recipes = pd.read_csv('data/recipes_df.csv')

recipes["ingredients_list"] = recipes["ingredients_list"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
recipes["ingredients_en"] = recipes["ingredients_en"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])

def format_time_to_minutes(time_str):
    if pd.isna(time_str):
        return None
    if 'h' in time_str:
        parts = time_str.split('h')
        hours = int(parts[0].strip())
        minutes = int(parts[1].strip().replace('min', '').strip()) if len(parts) > 1 and 'min' in parts[1] else 0
        return hours * 60 + minutes
    else:
        return int(time_str.replace('m', '').strip())
    

def people_served_to_int(servings_str):
    if pd.isna(servings_str):
        return None
    match = re.match(r'^\s*(\d{1,3})\s*(?:unidades?|comensales?)\s*$', servings_str, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


recipes["time"] = recipes["time"].apply(format_time_to_minutes)
recipes = recipes[recipes["ingredients"] != "[]"]
recipes = recipes[recipes["ingredients_en"].apply(len) > 2]
recipes["people_served"] = recipes["people_served"].apply(people_served_to_int)



recipes.to_csv('data/recipes_df.csv', index=False)
