from discord.ext import commands
import discord
import os, logging

logger = logging.getLogger(__name__)

# intents = discord.Intents.default()
intents = discord.Intents.all()
# intents.message_content = True
# intents.voice_states = True


class DiscordBot(commands.Bot):
    def __init__(
        self, command_prefix: str, intents: discord.Intents, status: discord.Status
    ):
        super().__init__(intents=intents, command_prefix=command_prefix, status=status)

    async def setup_hook(self):
        SERVERID = os.environ.get("SERVERID")
        vkenSERVERID = os.environ.get("VkenSERVERID")
        guild = discord.Object(id=int(SERVERID))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info(f"Commands synced to guild {SERVERID}")


        return await super().setup_hook()


# Botオブジェクト生成
bot = DiscordBot(intents=intents, command_prefix="!", status=discord.Status.online)
