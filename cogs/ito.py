import logging, logging, os, discord, re, random
from database.dbmanage import Dbmanage
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from database.dbmanage import Dbmanage

# ロガーの設定
logger = logging.getLogger(__name__)


class ItoCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ito")
    async def ito(self, interaction, members: str):
        await interaction.response.defer(thinking=True)
        count = len(members.split(" "))
        if count == 0:
            await interaction.response.send_message("メンバーが指定されていません")
            return
        random_numbers = random.sample(range(1, 100), count)
        for member in members.split(" "):
            member = member.strip()
            try:
                discord_member = await interaction.guild.fetch_member(int(re.sub(r"\D", "", member)))
                if discord_member is None:
                    await interaction.response.send_message(f"{member}はこのサーバーにいません")
                    return
                await discord_member.send(f"あなたの数字は{random_numbers.pop(0)}です")
            except Exception as e:
                print(e)
        await interaction.followup.send("メンバーに数字を送信しました")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if re.match(r"^\d+D\d+$", message.content):
            numbers = message.content.split("D")
            count = int(numbers[0])
            face = int(numbers[1])
            if count > 20 or face > 20:
                await message.channel.send("20D20までの数字を指定してください")
                return
            rolls = [random.randint(1, face) for _ in range(count)]
            total = sum(rolls)
            await message.reply(f"出目: {total}")
        return
        

# Cogを追加
async def setup(bot: commands.Bot):

    await bot.add_cog(ItoCog(bot))
