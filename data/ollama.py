import requests
import pandas as pd

df = pd.read_csv('yt_comments_dataset_v2.csv')
# df = df[df['sentiment'].isna() | (df['sentiment'] == "")]
OUTPUT_PATH = "yt_comment_datatest_v2_lang.csv"
BATCH_SIZE = 100
count = 1

if "lang" not in df.columns:
    df["lang"] = pd.NA

def gen_prompt(comment):
    return f'''
    Your task is to identify the given comment as english, or hinglish(code mixed hindi and english). 
    Answer in one word(english/hinglish)
    Comment: {comment}
    Answer:
            '''

def get_lang(response):
    lang = response.strip().lower()
    lang = lang.split()[-1]
    return lang

batch_indices = []
batch_langs = []

for idx, comment in df['comment'].items():
    print(f"processing comment {count}")
    prompt = gen_prompt(comment)
    try:
        response = requests.post('http://localhost:11434/api/generate',
                                json={"model": "qwen2.5:7b",
                                        "prompt": prompt,
                                        "stream": False})
        result = response.json()
        response = result['response']
        lang = get_lang(response)
    except Exception:
        lang = None

    batch_indices.append(idx)
    batch_langs.append(lang)

    if count % BATCH_SIZE == 0:
        df.loc[batch_indices, "lang"] = batch_langs
        df.to_csv(OUTPUT_PATH, index=False)
        batch_indices.clear()
        batch_langs.clear()

    count += 1

if batch_indices:
    df.loc[batch_indices, "lang"] = batch_langs

df.to_csv(OUTPUT_PATH, index=False)
