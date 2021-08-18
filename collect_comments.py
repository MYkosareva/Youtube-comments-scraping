from googleapiclient.discovery import build
import pandas as pd
from tqdm import tqdm

"""Collecting comments using Google API.
Let's take Varlamov's video as a basis:
'Почему Россия — не Израиль в мире прививок | Как теория заговора замедляет распространение Спутник V'
link for video: https://www.youtube.com/watch?v=fvUU943dhFY
"""

API_KEY = "xxxxx"  # input your API key (Follow instructions for getting key https://developers.google.com/youtube/v3/getting-started?hl=ru)
VIDEO_ID = "fvUU943dhFY"  # input video id (last symbols after '=' in video link)
comments_list = []


class Collect_Comments:
    def __init__(self, api_key, video_id):
        self.api_key = api_key
        self.video_id = video_id
        self.connection = build('youtube', 'v3', developerKey=self.api_key)

    def collect_comments(self, resp):
        for item in tqdm(resp['items']):
            name = item["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
            comment = item["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            published_at = item["snippet"]['topLevelComment']["snippet"]['publishedAt']
            likes = item["snippet"]['topLevelComment']["snippet"]['likeCount']
            replies = item["snippet"]['totalReplyCount']
            if [name, comment, published_at, likes, replies] not in comments_list:
                comments_list.append([name, comment, published_at, likes, replies])

            totalReplyCount = item["snippet"]['totalReplyCount']
            if totalReplyCount > 0:
                parent = item["snippet"]['topLevelComment']["id"]
                response_2 = self.connection.comments().list(part='snippet', maxResults='100', parentId=parent,
                                                             textFormat="plainText").execute()
                for i in response_2["items"]:
                    name = i["snippet"]["authorDisplayName"]
                    comment = i["snippet"]["textDisplay"]
                    published_at = i["snippet"]['publishedAt']
                    likes = i["snippet"]['likeCount']
                    replies = ""
                    if [name, comment, published_at, likes, replies] not in comments_list:
                        comments_list.append([name, comment, published_at, likes, replies])

    def save_to_csv(self, path_to_save_file):
        df = pd.DataFrame({'Name': [i[0] for i in comments_list], 'Comment': [i[1] for i in comments_list],
                           'Time': [i[2] for i in comments_list],
                           'Likes': [i[3] for i in comments_list], 'Reply Count': [i[4] for i in comments_list]})
        df.to_csv(path_to_save_file, index=False)
        return "Successful!2 Check the CSV file that you have just created."

    def get_comments(self, path_to_save_file):
        response = self.connection.commentThreads().list(part='snippet, replies', videoId=self.video_id).execute()
        self.collect_comments(response)
        while 'nextPageToken' in response:
            response = self.connection.commentThreads().list(part='snippet,replies', videoId=self.video_id,
                                                             pageToken=response["nextPageToken"]).execute()
            self.collect_comments(response)
        self.save_to_csv(path_to_save_file)
        print('Count of getting comments :  ', len(comments_list))


if __name__ == "__main__":
    path = ''                                       # path to save new csv file
    comments = Collect_Comments(API_KEY, VIDEO_ID)  # create an instance of the class
    comments.get_comments(path)                     # collect of comments