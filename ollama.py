import requests
import pandas as pd

df = pd.read_csv('data/comments.csv')
df = df.head(10)
dflang =[]
count = 1

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

for comment in df['comment']:
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
        dflang.append(lang)
    
    except:
        dflang.append(None)
        
    count += 1

df['lang'] = dflang

df.to_csv("yt_comment_datatest2.csv")