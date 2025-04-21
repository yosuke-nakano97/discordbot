import logging, logging, os, datetime, discord
from database.models import Booking
from database.dbmanage import Dbmanage
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from util import schedule
from cogs.ui import submit_form
from database.dbmanage import Dbmanage
from bot import bot

# ロガーの設定
logger = logging.getLogger(__name__)


class BookingCog(commands.Cog):

    def __init__(self, bot):
        load_dotenv()
        self.setup_reload()

    @app_commands.command(name="booking")
    async def book_make(self, interaction):
        logger.info("booking called by: %s", interaction.user.name)
        if interaction.user.bot:
            return

        booking = Booking()
        booking.id = interaction.id
        booking.user_id = interaction.user.id
        booking.channel_id = interaction.channel.id
        await interaction.response.send_message(
            "予約投稿のチャンネル選んでネ",
            view=submit_form.ChannelSelectView(booking),
            ephemeral=True,
        )

    async def remind(self, id):
        booking = Dbmanage().read_booking_by_id(id)
        logger.info("remind called by: %s", id)
        guild_id = os.getenv("SERVERID")
        guild = await bot.fetch_guild(guild_id)
        channel = await guild.fetch_channel(booking.channel_id)
        user = await guild.fetch_member(booking.user_id)
        if booking.target is None:
            await channel.send(f"{booking.message}\n{user.name}")
        else:
            if booking.role:
                role = guild.get_role(int(booking.target))
                await channel.send(
                    f"{role.mention}\n{booking.message}\n{user.name}{type(booking.target)}"
                )
            else:
                member = await guild.fetch_member(booking.target)
                await channel.send(f"{member.mention}\n{booking.message}\n{user.name}")

    @app_commands.command(name="edit_booking")
    async def edit(self, interaction):
        logger.info("edit called by: %s", interaction.user.name)
        if interaction.user.bot:
            return
        if interaction.user.get_role(960814188966588416) is None:
            await interaction.response.send_message(
                "仕事する気はないゴマ", ephemeral=True
            )
            return

        bookings = Dbmanage().read_booking_by_userid(interaction.user.id)
        if bookings is None:
            await interaction.response.send_message(
                "予約が見つかりませんでした", ephemeral=True
            )
            return
        print(type(bookings[0].message))

        await interaction.response.send_message(
            "予約投稿のターゲット選んでネ",
            view=submit_form.BookingSelectView(bookings),
            ephemeral=True,
        )

    @app_commands.command(name="reload_booking")
    async def reload(self, interaction, password: str):
        logger.info("reload called by: %s", interaction.user.name)
        passwd = os.getenv("PASSWORD")
        if interaction.user.bot:
            return
        if password != passwd:
            await interaction.response.send_message(
                "仕事する気ないゴマ", ephemeral=True
            )
            return

        bookings = Dbmanage().read_bookings()
        if bookings is None:
            await interaction.response.send_message(
                "予約が見つかりませんでした", ephemeral=True
            )
            return
        now = datetime.datetime.now()
        bookings = [booking for booking in bookings if booking.datetime >= now]
        bookings = [
            booking
            for booking in bookings
            if booking.datetime <= now + datetime.timedelta(days=60)
        ]
        if len(bookings) != 0:
            for booking in bookings:
                job = schedule.schedule.add_job(booking.datetime, booking.id)
                booking.job_id = job.id
                Dbmanage().update_booking(booking)

        await interaction.response.send_message(
            "リロード完了",
            ephemeral=True,
        )

    def setup_reload(self):
        logger.info("reload called by: bot")

        bookings = Dbmanage().read_bookings()
        if bookings is None:
            return

        now = datetime.datetime.now()
        bookings = [booking for booking in bookings if booking.datetime >= now]
        bookings = [
            booking
            for booking in bookings
            if booking.datetime <= now + datetime.timedelta(days=60)
        ]
        if len(bookings) != 0:
            for booking in bookings:
                job = schedule.schedule.add_job(booking.datetime, booking.id)
                booking.job_id = job.id
                Dbmanage().update_booking(booking)


# Cogを追加
async def setup(bot: commands.Bot):

    await bot.add_cog(BookingCog(bot))
