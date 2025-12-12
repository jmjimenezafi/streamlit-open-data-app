# flake8: noqa
# ruff: noqa
# pylint: skip-file

import pandas as pd
import ast
from ingredient_parser import parse_ingredient
from tqdm import tqdm

tqdm.pandas()

recipes = pd.read_csv('data/recipes_df.csv')


def convert_to_real_list(texto):
    if pd.isna(texto):
        return []
    
    try:
        if isinstance(texto, list):
            return texto
        return ast.literal_eval(str(texto))
    except:
        texto_limpio = str(texto).strip('[]')
        return [ing.strip().strip("'\"") for ing in texto_limpio.split("', '") if ing.strip()]

recipes["ingredients_en"] = recipes["ingredients_en"].apply(convert_to_real_list)



def parse_ingredients_list(ingredients_list):
    parsed_ingredients = []
    for ing in ingredients_list:
        if isinstance(ing, str) and ing.strip():
            try:
                parsed = parse_ingredient(ing.strip())
                parsed_ingredients.append(parsed.name[0].text.lower().strip())
            except:
                parsed_ingredients.append(ing.lower().strip())
    return parsed_ingredients


recipes["ingredients_list"] = recipes["ingredients_en"].progress_apply(parse_ingredients_list)


recipes.to_csv('data/recipes_df.csv', index=False)