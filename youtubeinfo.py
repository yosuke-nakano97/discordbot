import os

from googleapiclient.discovery import build


class YouTubeInfo:
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    QUOTA_INITIAL = 10000

    def __init__(self):
        self.quota = 10000
        self.developerkey = os.environ.get("YOUTUBE_API_KEY1", None)

    def CheckQuotaRemain(self):
        if self.quota > 100:
            return True
        else:
            return False

    def BuildApiService(self):
        return build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            developerKey=self.developerkey,
        )

    def QuotaSub(self, minus):
        self.quota -= minus

    def QuotaReset(self):
        self.quota = self.QUOTA_INITIAL
