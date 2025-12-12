# flake8: noqa
# ruff: noqa
# pylint: skip-file

import pandas as pd


recipes = pd.read_csv('data/recipes_df.csv')


def format_nutritional_info(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return value

    value = str(value).strip()

    value = (value.replace("kcal", "")
                 .replace("g", "")
                 .replace(".", "")
                 .replace(",", "."))

    try:
        return float(value)
    except ValueError:
        return None



recipes["Calorías"] = recipes["Calorías"].apply(format_nutritional_info)
recipes["Grasas"] = recipes["Grasas"].apply(format_nutritional_info)
recipes["Carbohidratos"] = recipes["Carbohidratos"].apply(format_nutritional_info)
recipes["Proteínas"] = recipes["Proteínas"].apply(format_nutritional_info)
recipes["Fibra"] = recipes["Fibra"].apply(format_nutritional_info)

recipes["Calorías"] = pd.to_numeric(recipes["Calorías"], errors='coerce')
recipes["Grasas"] = pd.to_numeric(recipes["Grasas"], errors='coerce')
recipes["Carbohidratos"] = pd.to_numeric(recipes["Carbohidratos"], errors='coerce')
recipes["Proteínas"] = pd.to_numeric(recipes["Proteínas"], errors='coerce')
recipes["Fibra"] = pd.to_numeric(recipes["Fibra"], errors='coerce')

recipes.to_csv('data/recipes_df.csv', index=False)
