# モジュールのインポート
import asyncio
import json
import logging
import logging.config
import os
from bot import bot
from dotenv import load_dotenv

from youtubeinfo import YouTubeInfo

with open("log_config.json", "r") as f:
    config = json.load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

logger.info("Starting the bot")

# Cogのリスト
INITIAL_EXTENSIONS = [ "cogs.ito", "cogs.quiz"]

# .envから各種変数読み出し
load_dotenv(override=True)

youtube = YouTubeInfo()


@bot.event
async def on_ready():
    logger.info(f"We have logged in as {bot.user}")



@bot.event
async def on_guild_join(guild):
    logger.info(f"Bot has joined {guild.name}")
    my_guild = os.environ.get("SERVERID")
    if guild.id != int(my_guild):
        await guild.leave()
        logger.info(f"Bot has left {guild.name}")


# Botのセットアップ
async def main():
    async with bot:
        # Cogをロード
        for cog in INITIAL_EXTENSIONS:
            await bot.load_extension(cog)

        # Botを起動
        BOTTOKEN = os.environ.get("BOTTOKEN")
        if not BOTTOKEN:
            raise ValueError("環境変数 'BOTTOKEN' が設定されていません。")
        await bot.start(BOTTOKEN)  # Botを非同期で起動


# メインイベントループの実行
if __name__ == "__main__":
    asyncio.run(main())
