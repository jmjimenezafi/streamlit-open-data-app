# flake8: noqa
# ruff: noqa
# pylint: skip-file
 
import asyncio
import aiohttp
import pandas as pd
from tqdm import tqdm
import time

recipes = pd.read_csv('data/recipes.csv')

async def translate_text(session, text, source='es', target='en', api_url='http://localhost:5000/translate'):
    payload = {'q': text, 'source': source, 'target': target}
    async with session.post(api_url, data=payload) as resp:
        if resp.status == 200:
            return (await resp.json())['translatedText']
        else:
            return text

async def translate_list_async(texts, batch_size=50):
    translated_texts = []
    total = len(texts)
    
    async with aiohttp.ClientSession() as session:
        for i in tqdm(range(0, total, batch_size), desc="Batches"):
            batch = texts[i:i+batch_size]
            start_time = time.time()
            
            # Traducción concurrente de este batch
            results = await asyncio.gather(*[translate_text(session, t) for t in batch])
            translated_texts.extend(results)
            
            batch_time = time.time() - start_time
            print(f"Batch {i//batch_size + 1} de {((total-1)//batch_size + 1)} completado en {batch_time:.2f}s")
    
    return translated_texts

if __name__ == "__main__":

    recipes = pd.read_csv("data/recipes.csv")
    
    texts = recipes["ingredients"].tolist()
    
    translated = asyncio.run(translate_list_async(texts, batch_size=100))
    
    recipes["ingredients_en"] = translated
    
    recipes.to_csv("data/recipes_df.csv", index=False)