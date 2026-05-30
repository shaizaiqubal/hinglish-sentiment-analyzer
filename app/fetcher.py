from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube','v3',developerKey=key)

def fetch_data(url, max_comments=500):

    parsed = urlparse(url)

    if not parsed.netloc:
        pass
    else:
        vid_id = parse_qs(parsed.query)['v'][0]

    #fetch title
    req_title = youtube.videos().list(part = 'snippet',id = vid_id)
    res_title = req_title.execute()
    title = res_title['items'][0]['snippet']['title']

    if not title:
        return vid_id, None, []
    
    #fetch comments
    comments = []
    count = 0
    next_page_token = None

    while count < max_comments:
        req_comments = youtube.commentThreads().list(
            part="snippet",
            videoId=vid_id,
            textFormat="plainText",
            pageToken=next_page_token,
            maxResults=100,
            order='relevance'
        )

        res_comments = req_comments.execute()

        if not res_comments['items']:
            return vid_id, title, []
        
        else:

            for item in res_comments['items']:
                comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment_text)
                count += 1

                if count >= max_comments:
                    break

            next_page_token = res_comments.get('nextPageToken')

            if not next_page_token:
                break

    return vid_id, title, comments
