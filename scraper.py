import csv
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube','v3',developerKey=key)

#urls =[]
#vid_ids= ['0IZS7ucM9qQ','znefLMNyVE8','nxUcxHMEUGg','QedpcsA-GOU','BKOVzHcjEIo','NHk7scrb_9I','5XVoRGhrhZk','edx_qdEBAf0','g0CWxEuN2VI','RXeLbs_ogDU','uQoDmiMoXHg','8z_YVi-NycI','8YP81X1Jur4','xvvZATxs30M','vpNC1qM_cCE','zzwRbKI2pn4']
vid_ids=["lFe5OA6uN8g","C3_mYPlvJeE","dpIJHTIEKC0",'ADllavPbUsg','WshNJefWEP8','WhvuONO1INQ','TNPtBnM4koE','QE6tkqvYW4']


# for i in urls:
#      parsed = urlparse(i)
#      params = parse_qs(parsed.query)
#      vid = params['v'][0]
#      vid_ids.append(vid)

     


csv_exists = os.path.exists('yt_comment_dataset_v2.csv')

with open('yt_comment_dataset.csv', 'a' if csv_exists else 'w') as dataset:
    writer = csv.writer(dataset)

    for i in range(len(vid_ids)):

        if not csv_exists:
            writer.writerow(['video_id', 'comment', 'likes'])

        vid_id = vid_ids[i]
        print(f'scraping {vid_id}....')

        # req_title = youtube.videos().list(part = "snippet", id=vid_id)
        # res_title = req_title.execute()
        # vid_title = res_title['items'][0]['snippet']['title']
        count = 0
        next_page_token = None
        try:
            while True:
                    
                    
                    req_comments = youtube.commentThreads().list(
                    part='snippet',
                    videoId=vid_id,
                    textFormat='plainText',
                    pageToken=next_page_token,
                    order='relevance'
                    )

                    res_comments = req_comments.execute()

                    for item in res_comments['items']:
                        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                        comment = comment.replace('\n','')
                        likes = int(item['snippet']['topLevelComment']['snippet']['likeCount'])
                        writer.writerow([vid_id, comment, likes])
                        count+=1


                    next_page_token = res_comments.get('nextPageToken')

                    if not next_page_token:
                        break

                    if count >= 1000:
                         break
        
        except Exception as e:
            print(f"Error encountered at id {vid_id} : {e}")
            continue                            

print('================DONE==================')