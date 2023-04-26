from googlesearch import search
import aiohttp
import asyncio
import nest_asyncio #what is this for??
import re
import openai
import time

# openai.api_key = "your_openai_api_key"
def get_search_results(query, num_results=10):
    search_results = [j for j in search(query, num_results=num_results)]
    return search_results

import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        paragraphs = [p.get_text() for p in paragraphs]
        content = '\n'.join([p for p in paragraphs if len(p) > 50])

        # content = '\n'.join([paragraph.get_text() for paragraph in paragraphs])
        return content
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""

# from bs4 import BeautifulSoup

async def extract_text_from_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                paragraphs = soup.find_all('p')
                content = '\n'.join([paragraph.get_text() for paragraph in paragraphs])
                return content
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""

async def fetch_all_texts(urls):
    tasks = [asyncio.ensure_future(extract_text_from_url(url)) for url in urls]
    extracted_texts = await asyncio.gather(*tasks)
    return extracted_texts

def get_extracted_texts(search_results):
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    extracted_texts = loop.run_until_complete(fetch_all_texts(search_results))
    return extracted_texts

def preprocess_text(text):
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove non-alphanumeric characters
    text = re.sub(r'\W', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

#old & useless, deprecate
def generate_answer(prompt, model="text-davinci-003", max_tokens=150):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
        # stream=True
    )

    answer = response.choices[0].text.strip()
    return answer

#better for streaming, more likely target
def _generate_answer(prompt, model="text-davinci-003", max_tokens=150):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
        stream=True,
    )

    return response
def search_user_input():
    query = get_user_query()
    start_time = time.time()

    print('searching...')
    search_results = get_search_results(query)

    print(f'extracting after {time.time() - start_time}...')
    extracted_texts = get_extracted_texts(search_results[:5])

    print(f'preprocessing after {time.time() - start_time}...')
    preprocessed_texts = [preprocess_text(text)[:400] for text in extracted_texts]

    print(f'generating after {time.time() - start_time}...')
    combined_text = '\n'.join(preprocessed_texts)
    prompt = f"Please answer the following question based on the information provided: {query}\n\n{combined_text}\n"
    gen = _generate_answer(prompt)

    print(f'first token after {time.time() - start_time}...')
    for chunk in gen:
        ch = chunk['choices'][0]['text']#['delta'].get('content', '')
        print(ch, end="", flush=True)

class WebSearch:
    pass
