# flake8: noqa
# ruff: noqa
# pylint: skip-file

from time import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

class Recipe_scraper:
    def __init__(self):
        self.url = 'https://www.recetasgratis.net/'
        self.categories = []

    def scrape_categories(self, main_page_soup):
        for category_div in main_page_soup.select('div.categoria'):
            category_a = category_div.select('a.titulo')
            if category_a:
                category_a = category_a[0]
                category_name = category_a.get_text(strip=True)
            
                for subcat_li in category_div.select('ul.sub-categorias li'):
                    subcat_name = subcat_li.get_text(strip=True)
                    subcat_url = subcat_li.find('a')['href']
                    self.categories.append({
                        'category': category_name,
                        'subcategory': subcat_name,
                        'url': subcat_url
                    })

            continue

        self.categories_df = pd.DataFrame(self.categories)


    def scrape_recipes(self, url):
        main_page_response = requests.get(url)
        main_page_soup = BeautifulSoup(main_page_response.content, 'html.parser')

        self.scrape_categories(main_page_soup)
        all_recipes = []
        
        for index, row in self.categories_df.iterrows():
            subcat_url = row['url']

            while subcat_url:
                subcat_html = requests.get(subcat_url)
                recipes = self.get_recipes_from_page(subcat_html, category_name=row['category'], subcat_name=row['subcategory'])
                all_recipes.extend(recipes)

                subcat_url = self.get_next_pages(subcat_html.content)


        recipes_df = pd.DataFrame(all_recipes).drop_duplicates('recipe_name')
        recipes_df.to_csv('data/recipes.csv', index=False)

        return recipes_df

    def get_next_pages(self, subcat_html):
        current_url_soup = BeautifulSoup(subcat_html, 'html.parser')

        if current_url_soup.select_one('div.paginator_wrap a.next'):
            next_page_url = current_url_soup.select_one('div.paginator_wrap a.next')['href']
            return next_page_url
        return None
    
    def get_recipes_from_page(self, subcat_html, category_name=None, subcat_name=None):
        current_subcat_soup = BeautifulSoup(subcat_html.content, 'html.parser')
        recipes = []

        for recipe_container in current_subcat_soup.select('section.resultados div.resultado'):
            recipe_name = recipe_container.select_one('a.titulo').get_text(strip=True)
            recipe_url = recipe_container.select_one('a.titulo')['href']

            recipe_html = requests.get(recipe_url)

            people_served    = self.get_people_served(recipe_html)
            time             = self.get_time(recipe_html)
            type_of_dish     = self.get_type_of_dish(recipe_html)
            difficulty       = self.get_difficulty(recipe_html)
            ingredients      = self.get_ingredients(recipe_html)

            recipes.append({
                'category': category_name,
                'subcategory': subcat_name,
                'recipe_name': recipe_name,
                'recipe_url': recipe_url,
                'people_served': people_served,
                'time': time,
                'type_of_dish': type_of_dish,
                'difficulty': difficulty,
                'ingredients': ingredients
            })

            nutritional_info = self.get_nutritional_info(recipe_html)
            for key, value in nutritional_info.items():
                recipes[-1][key] = value

        return recipes

    def get_people_served(self, recipe_html):
        recipe_soup = BeautifulSoup(recipe_html.content, 'html.parser')
        people_served = recipe_soup.select_one('div.properties span:first-child')

        if people_served:
            return people_served.get_text(strip=True)
        return None
    
    def get_time(self, recipe_html):
        recipe_soup = BeautifulSoup(recipe_html.content, 'html.parser')
        time_info = recipe_soup.select_one('div.properties span.duracion')

        if time_info:
            return time_info.get_text(strip=True)
        return None
    
    def get_type_of_dish(self, recipe_html):
        recipe_soup = BeautifulSoup(recipe_html.content, 'html.parser')
        type_of_dish = recipe_soup.select_one('div.properties span.para')

        if type_of_dish:
            return type_of_dish.get_text(strip=True)
        return None

    def get_difficulty(self, recipe_html):
        recipe_soup = BeautifulSoup(recipe_html.content, 'html.parser')
        difficulty = recipe_soup.select_one('div.properties span.dificultad')

        if difficulty:
            return difficulty.get_text(strip=True)
        return None

    def get_ingredients(self, recipe_html):
        recipe_soup = BeautifulSoup(recipe_html.content, 'html.parser')
        ingredients = []

        for ingredient_li in recipe_soup.select('div.ingredientes li.ingrediente label'):
            ingredient_quantity_and_name = ingredient_li.get_text(strip=True)
            ingredients.append(ingredient_quantity_and_name)

        return ingredients
    
    def get_nutritional_info(self, recipe_html):
        recipe_soup = BeautifulSoup(recipe_html.content, 'html.parser')
        nutritional_info = {}

        for nutrition_li in recipe_soup.select('div#nutritional-info ul li'):
            if ':' in nutrition_li.get_text():
                label, value = nutrition_li.get_text(strip=True).split(':', 1)
            nutritional_info[label.strip()] = value.strip() 

        return nutritional_info


main = Recipe_scraper()
main.scrape_recipes(main.url)