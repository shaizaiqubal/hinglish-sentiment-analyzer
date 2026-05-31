from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube','v3',developerKey=key)

def extract_video_id(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")

    if not host:
        return None

    if "youtu.be" in host:
        return path.split("/")[0] if path else None

    if "youtube.com" in host:
        query_video_id = parse_qs(parsed.query).get("v")
        if query_video_id:
            return query_video_id[0]

        path_parts = [part for part in path.split("/") if part]
        if len(path_parts) >= 2 and path_parts[0] in {"shorts", "embed", "live"}:
            return path_parts[1]

    return None

def fetch_data(url, max_comments=500):
    vid_id = extract_video_id(url)
    if not vid_id:
        return None, None, []

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
