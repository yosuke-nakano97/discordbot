import logging
import os

import requests
from dotenv import find_dotenv, load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import database.dbmanage as db
from database.models import Channel_Y
from youtubeinfo import YouTubeInfo

load_dotenv(override=True)
# Set up logging
logger = logging.getLogger(__name__)


class urlprocesser:

    def __init__(self):

        self.youtube = YouTubeInfo()

        self.api = self.youtube.BuildApiService()

    def domain_check(self, url):
        domain = None
        logger.debug(f"Processing URL: {url}")
        try:
            if url != "":
                domain = url.split("/")[2]
                logger.debug(f"Domain: {domain}")

        except IndexError:
            logger.error("URL is invalid")
            return None, None

        if "youtube.com" in url or "youtu.be" in url:

            return "youtube", domain

        elif "twitter.com" in url or "x.com" in url:

            return "x", domain

        else:

            return None, domain

    def youtube_analyze(self, url):

        answer = []

        handle = None

        post_id = None

        channel_id = None

        video_id = None

        flag = False

        # urlのタイプを特定

        if "post" in url:
            post_id = url.split("post/")[-1].split("?")[0].split("&")[0]
            logger.debug(f"Post ID: {post_id}")

        if "list=" in url:
            list_id = url.split("list=")[-1].split("?")[0].split("&")[0]
            logger.debug(f"List ID: {list_id}")
            flag = True

        if "v=" in url:
            video_id = url.split("v=")[-1].split("?")[0].split("&")[0]
            logger.debug(f"Video ID: {video_id}")
            flag = True

        if "live/" in url:
            video_id = url.split("live/")[-1].split("?")[0].split("&")[0]
            logger.debug(f"video ID: {video_id}")
            flag = True

        if "shorts/" in url:
            video_id = url.split("shorts/")[-1].split("?")[0].split("&")[0]
            logger.debug(f"video ID: {video_id}")
            flag = True

        if "channel/" in url:
            channel_id = (
                url.split("channel/")[-1].split("?")[0].split("&")[0].split("/")[0]
            )
            logger.debug(f"Channel ID: {channel_id}")
            flag = True

        if "@" in url:
            handle = url.split("@")[-1].split("?")[0].split("&")[0].split("/")[0]
            logger.debug(f"Handle: {handle}")
            flag = True

        if "clip/" in url:
            video_id = url.split("clip/")[-1].split("?")[0].split("&")[0]
            logger.debug("this is clip")

        if "youtu.be" in url:

            video_id = url.split("/")[-1].split("?")[0].split("&")[0]

            logger.debug(f"video ID: {video_id}")

            flag = True

        # もし特定可能なタグならば

        if flag:
            # 持っているタグ種別で分類
            if video_id:

                channel_id = self.get_video_info(video_id)

                # チャンネルが見つからなかった場合
                if channel_id == None:
                    return False, url

            if channel_id:
                answer.append(self.get_channel_info(channel_id))

            elif handle:
                answer.append(self.get_channel_info(handle=handle))

            elif list_id:
                try:
                    respond = (
                        self.api.playlistItems()
                        .list(part="contentDetails", playlistId=list_id, maxResults=50)
                        .execute()
                    )
                except HttpError as e:
                    logger.error("HTTP error %d: %s", e.resp.status, e.content)
                    return False, url

                for item in respond["items"]:
                    video_id = item["contentDetails"]["videoId"]
                    channel_id = self.get_video_info(video_id)

                    if channel_id != None:
                        answer.append(self.get_channel_info(channel_id))

                while "nextPageToken" in respond:
                    respond = (
                        self.api.playlistItems()
                        .list(
                            part="contentDetails",
                            playlistId=list_id,
                            maxResults=50,
                            pageToken=respond["nextPageToken"],
                        )
                        .execute()
                    )

                    for item in respond["items"]:

                        video_id = item["contentDetails"]["videoId"]
                        channel_id = self.get_video_info(video_id)

                        answer.append(self.get_channel_info(channel_id))

            return flag, answer

        else:

            return flag, url

    def get_channel_info(self, channel_id=None, handle=None):

        channel_info = Channel_Y()
        respond = None

        if channel_id == None and handle == None:
            channel_info.id = "deleted"
            channel_info.name = "deleted"
            channel_info.icon = "deleted"
            return channel_info

        try:
            if channel_id:
                respond = (
                    self.api.channels()
                    .list(part="snippet,contentDetails,statistics", id=channel_id)
                    .execute()
                )

            elif handle:
                respond = (
                    self.api.channels()
                    .list(part="snippet,contentDetails,statistics", forHandle=handle)
                    .execute()
                )

        except HttpError as e:
            logger.error("An HTTP error %d occurred:\n%s", e.resp.status, e.content)
            logger.info("Channel ID: %s", channel_id)
            logger.info("Handle: %s", handle)

        if respond["pageInfo"]["totalResults"] == 0:
            channel_info.id = "deleted"
            channel_info.name = "deleted"
            channel_info.icon = "deleted"

            return channel_info

        channel_info.id = respond["items"][0]["id"]

        channel_info.name = respond["items"][0]["snippet"]["title"]

        channel_info.icon = respond["items"][0]["snippet"]["thumbnails"]["default"][
            "url"
        ]

        return channel_info

    def get_video_info(self, video_id):
        try:
            respond = self.api.videos().list(part="snippet", id=video_id).execute()

            # print(respond["items"])
            if respond["items"] == []:
                return None

            channel_id = respond["items"][0]["snippet"]["channelId"]
            return channel_id
        except HttpError as e:
            logger.error("An HTTP error %d occurred:\n%s", e.resp.status, e.content)
            logger.info("Video ID: %s", video_id)
            return None

    def get_twitter_id(self, url):
        id = url.split("/")[3]
        return id
