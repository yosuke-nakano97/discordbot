import logging, logging, os
from database.dbmanage import Dbmanage
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from database.dbmanage import Dbmanage

# ロガーの設定
logger = logging.getLogger(__name__)


class AdminCog(commands.Cog):

    def __init__(self, bot):
        load_dotenv()

    @app_commands.command(name="save_roles")
    async def save_roles(self, interaction, password: str):
        logger.info("save_roles called by: %s", interaction.user.name)
        if interaction.user.id != int(os.getenv("OWNER")):
            await interaction.response.send_message("仕事する気ないゴマ")
            return
        if password != os.getenv("PASSWORD"):
            await interaction.response.send_message("パスワード違うよ")
            return

        roles = interaction.user.roles
        Dbmanage().save_roles(roles)
        await interaction.response.send_message("保存したよ", ephemeral=True)

    @app_commands.command(name="load_roles")
    async def load_roles(self, interaction, password: str):
        logger.info("load_roles was called by: %s", interaction.user.name)
        if interaction.user.id != int(os.getenv("OWNER")):
            await interaction.response.send_message("仕事する気ないゴマ")
            return
        if password != os.getenv("PASSWORD"):
            await interaction.response.send_message("パスワード違うよ")
            return
        await interaction.response.defer(ephemeral=True)
        roles = Dbmanage().load_roles()
        user = interaction.user
        for role in roles:
            role = interaction.guild.get_role(role.id)
            if role.name == "@everyone":
                continue
            await user.add_roles(role)
        await interaction.followup.send("ロールを付与したよ", ephemeral=True)

    @app_commands.command(name="echo")
    async def echo(self, interaction, message: str):
        logger.info("echo was called by: %s", interaction.user.name)
        await interaction.response.send_message(message)


# Cogを追加
async def setup(bot: commands.Bot):

    await bot.add_cog(AdminCog(bot))
