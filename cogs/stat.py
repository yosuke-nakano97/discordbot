import asyncio
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from logging import getLogger

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from database.dbmanage import Dbmanage
from database.models import Message, User, engine
from util.urlprocesser import urlprocesser

# ロガーの設定
logger = logging.getLogger(__name__)


class StatCog(commands.Cog):

    def __init__(self, bot):

        from vken import youtube

        self.youtube = youtube
        self.db = Dbmanage()

        load_dotenv()

        self.bot = bot

    # @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="get_stat")
    async def get_stat(self, interaction, password: str):

        logger.info("get_stat called by: %s", interaction.user.name)

        if password != os.environ.get("PASSWORD"):

            await interaction.response.send_message(
                "パスワードが違います", ephemeral=True
            )
            logger.info("get_stat finished with wrong password")
            return

        await interaction.response.defer(ephemeral=True)
        logger.info("get_stat deferred response")

        txtchannels = [
            channel
            for channel in interaction.guild.channels
            if isinstance(channel, discord.TextChannel)
        ]

        theads = [thread for channel in txtchannels for thread in channel.threads]

        txtchannels.extend(theads)

        forumchannels = [
            channel
            for channel in interaction.guild.channels
            if isinstance(channel, discord.ForumChannel)
        ]

        theads = [thread for channel in forumchannels for thread in channel.threads]

        txtchannels.extend(theads)

        tasks = [self.get_channel_message(channel) for channel in txtchannels]

        await asyncio.gather(*tasks)

        # await self.get_channel_message(interaction.channel)

        logger.info("get_stat finished successfully")

        await interaction.followup.send("stat get")

    async def get_channel_message(self, channel):

        try:

            async for message in channel.history(limit=None):

                user = message.author.name
                time = message.created_at
                id = message.id
                url = ""
                channel_id = channel.id
                channel_name = channel.name
                category = channel.category
                print(category)
                if "http" in message.content:

                    url = re.findall(r"http[^\s]*", message.content)[0]

                Dbmanage().reg_message(user, time, url, id, channel_id, channel_name, category)

        except SyntaxError as e:
            logger.info(f"Error fetching messages from {channel.name}: {e}")

            print(f"Error fetching messages from {channel.name}: {e}")

    # @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="make_stat")
    async def make_stat(self, interaction, password: str):
        logger.info("make_stat called by: %s", interaction.user.name)

        # 　パスワード確認

        if password != os.environ.get("PASSWORD"):
            logger.warning("make_stat failed due to incorrect password")
            await interaction.response.send_message(
                "パスワードが違います", ephemeral=True
            )
            return

        # 処理のために一旦レスポンスを返す

        await interaction.response.defer(ephemeral=True)
        logger.info("make_stat deferred response")

        messages = Dbmanage().read_message()

        for message in messages:
            try:
                url = message.url
                up = urlprocesser()
                db = Dbmanage()

                domain = up.domain_check(url)

                if domain[0] == "youtube":

                    if self.youtube.CheckQuotaRemain():

                        self.youtube.QuotaSub(1)

                    else:
                        await interaction.followup.send("youtube quota exceeded")

                        return 0

                    info = up.youtube_analyze(url)
                    logger.info("youtube_analyze completed successfully")

                    if info[0]:

                        for channel in info[1]:

                            db.reg_channel_y(channel, message.id)
                            db.reg_domain(domain[1])

                    else:

                        db.change_status(message.id, "youtube")

                elif domain[0] == "x":
                    id = up.get_twitter_id(url)
                    db.reg_twitter(message.id, id)
                    db.reg_domain(domain[1])
                    db.change_status(message.id, "success")

                else:
                    if domain[1] is not None:
                        db.reg_domain(domain[1])
                    db.change_status(message.id, "success")
            finally:
                pass
                # db.reg_domain(domein[1])

        logger.info("make_stat completed successfully")
        await interaction.followup.send("make stat")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type == discord.MessageType.new_member and message.author.id == 852518336603357234:
            await message.delete()
        return
        
        if message.author.bot:
            return
        
        try:
            user = message.author.name

            time = message.created_at

            id = message.id

            url = ""

            channel_id = message.channel.id

            channel_name = message.channel.name
            category = message.channel.category

            if "http" in message.content:

                url = re.findall(r"http[^\s]*", message.content)[0]

            Dbmanage().reg_message(user, time, url, id, channel_id, channel_name, category)
            logger.info(
                "Message received from %s at %s with id %s in channel %s",
                user,
                time,
                id,
                channel_name,
            )

        except Exception as e:
            logger.error("Error fetching messages from %s: %s",
                         message.channel.name, e)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        member_id = member.id
        time = datetime.now(timezone(timedelta(hours=9)))
        if before.channel == after.channel:
            return
        if after.channel != None:
            status = "join"
            self.db.reg_voice(member, after.channel, status)
        if before.channel != None:
            status = "exit"
            self.db.reg_voice(member, before.channel, status)


async def setup(bot: commands.Bot):

    await bot.add_cog(StatCog(bot))
