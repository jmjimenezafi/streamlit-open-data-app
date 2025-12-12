# flake8: noqa
# ruff: noqa
# pylint: skip-file

import json 
from rapidfuzz import process, fuzz
import pandas as pd
from tqdm import tqdm
import ast
import re

tqdm.pandas()

with open("C:\\Users\\juaji\\AFI\\AA_entregas_afi\\OPEN DATA\\data\\allergens_dict.json") as f:
    allergy_dict = json.load(f)

recipes = pd.read_csv("C:\\Users\\juaji\\AFI\\AA_entregas_afi\\OPEN DATA\\data\\recipes_df.csv")
recipes.head()


def convert_to_real_list(texto):
    if pd.isna(texto):
        return []
    try:
        if isinstance(texto, list):
            return texto
        return ast.literal_eval(str(texto))
    except:
        texto_limpio = str(texto).strip('[]')
        return [ing.strip().strip("'\"") for ing in texto_limpio.split(",") if ing.strip()]
    
recipes["ingredients_en"] = recipes["ingredients_en"].apply(convert_to_real_list)
recipes["ingredients" ]= recipes["ingredients"].apply(convert_to_real_list)
recipes["ingredients_list"] = recipes["ingredients_list"].apply(convert_to_real_list)



def clean_ingredient(ingredient):
    ingredient = str(ingredient).lower()
    ingredient = re.sub(r"[\[\]'\"()]", "", ingredient)
    ingredient = re.sub(r"\s+", " ", ingredient)
    return ingredient.strip()

recipes["ingredients_en"] = recipes["ingredients_en"].apply(
    lambda lst: [clean_ingredient(i) for i in lst]
)
recipes["ingredients"] = recipes["ingredients"].apply(
    lambda lst: [clean_ingredient(i) for i in lst]
)
recipes["ingredients_list"] = recipes["ingredients_list"].apply(
    lambda lst: [clean_ingredient(i) for i in lst]
)



def fuzzy_search_allergens(ingredient, allergy_dict, score_cutoff=90):
    ingredient = clean_ingredient(ingredient)  
    
    found_allergens = set()
    

    allergens = [a for allergen_list in allergy_dict.values() for a in allergen_list]
    

    matches = process.extract(
        ingredient,
        allergens,
        scorer=fuzz.WRatio,
        score_cutoff=score_cutoff,
        limit=None
    )
    
    for m in matches:
        found_allergens.add(m[0])
    

    found_allergies = set()
    for allergy, allergen_list in allergy_dict.items():
        if any(fa in allergen_list for fa in found_allergens):
            found_allergies.add(allergy)
    
    return list(found_allergies)



def detect_allergies(ingredient_list):
    found = set()
    for ing in ingredient_list:
        for allergy in fuzzy_search_allergens(ing, allergy_dict):
            found.add(allergy)
    return list(found)

recipes["detected_allergies"] = recipes["ingredients_en"].progress_apply(detect_allergies)
recipes.to_csv("C:\\Users\\juaji\\AFI\\AA_entregas_afi\\OPEN DATA\\data\\recipes_df.csv", index=False)