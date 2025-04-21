import asyncio, logging, random, os

# discord.pyのライブラリ
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

# 読み上げ機能のためのライブラリ
import voicevox_core
from voicevox_core import (
    AccelerationMode,
    AudioQuery,
    OpenJtalk,
    Synthesizer,
    VoiceModel,
)

# ロガーの設定
logger = logging.getLogger(__name__)


# VC関連の機能のためのCog
class VoiceCog(commands.Cog):

    def __init__(self, bot):
        load_dotenv()
        self.listening = False
        self.pause = False
        self.voice = None
        self.synthesizer = None
        self.style_id = 2
        self.channel_id = 1181808383800639552
        self.id = None
        self.synthesizer = None
        asyncio.create_task(self.setup_model())

    # BotくんがVCに参加するコマンド
    @app_commands.command(name="vyo_join")
    async def join(self, interaction):
        logger.info("vyo_join by: %s", interaction.user.name)
        # 人間が使ってるか確認
        if interaction.user.bot:
            return
        # VCに入ってるか確認
        if interaction.user.voice is None:
            await interaction.response.send_message("入ってないじゃん")
            return

        # VCに接続
        voicechannel = interaction.user.voice.channel
        self.voice = await voicechannel.connect(reconnect=True)
        self.listening = True
        await interaction.response.send_message(f"Connected to {voicechannel}")

    # BotくんがVCから退出するコマンド
    @app_commands.command(name="vyo_leave")
    async def leave(self, interaction):
        logger.info("get_stat called by: %s", interaction.user.name)
        if interaction.user.bot:
            return
        # 接続を切断
        self.listening = False
        await self.voice.disconnect()
        await interaction.response.send_message("Disconnected")

    # モデルと読み上げチャンネルをセットアップするコマンド
    @app_commands.command(name="vyo_setup")
    async def set_up(self, interaction, id: int, channel: discord.TextChannel):
        # 時間がかかることがあるから、待機時間の延長
        await interaction.response.defer(ephemeral=True)
        logger.info("get_stat called by: %s", interaction.user.name)
        if interaction.user.bot:
            return
        # モデルのIDと読み上げ名の対応表
        id_dict = {1: 2, 2: 3, 3: 8, 4: 14}
        # 読み上げ用チャンネルの設定
        self.channel_id = channel.id
        self.pause = True
        # モデルがなければセットアップ、あればIDのみ変更
        if self.synthesizer is None:
            self.synthesizer = await self.make_model()
            self.style_id = id_dict[id]
        else:
            self.style_id = id_dict[id]
        self.pause = False
        # 完了メッセージ
        await interaction.followup.send("Set up with " + str(id))

    # 使用可能なモデル一覧を表示するコマンド
    @app_commands.command(name="show_models")
    async def show_models(self, interaction):
        logger.info("get_stat called by: %s", interaction.user.name)
        if interaction.user.bot:
            return
        # モデルのIDと読み上げ名の対応を返す
        await interaction.response.send_message(
            "ID：読み上げ名\n1：四国めたん\n2：ずんだもん\n3：春日部つむぎ\n4：冥鳴ひまり"
        )

    # VCに入ってる人全員ミュートするテロ機能
    @app_commands.command(name="mute")
    async def mute(self, interaction):
        # どんだけ時間かかるかわからないから、待機時間の延長
        await interaction.response.defer(ephemeral=True)
        logger.info("get_stat called by: %s", interaction.user.name)
        if interaction.user.bot:
            return
        if interaction.user.voice is None:
            await interaction.followup.send("入ってないじゃん")
            return
        # VCに入ってる人を全員特定してミュート
        all_members = interaction.user.voice.channel.members
        for member in all_members:
            await member.edit(mute=True)
        await interaction.followup.send("Muted")

    # ミュートを解除するコマンド
    @app_commands.command(name="unmute")
    async def unmute(self, interaction):
        await interaction.response.defer(ephemeral=True)
        logger.info("get_stat called by: %s", interaction.user.name)
        if interaction.user.bot:
            return
        if interaction.user.voice is None:
            await interaction.followup.send("入ってないじゃん")
            return
        voice_channel = interaction.user.voice.channel
        all_members = voice_channel.members
        for member in all_members:
            await member.edit(mute=False)
        await interaction.followup.send("Unmuted")

    # メッセージ送信を監視、音声生成
    @commands.Cog.listener()
    async def on_message(self, message):
        # メッセージがBot、反応禁止なコマンド利用、一時停止、読み上げチャンネル以外
        # VC接続してない、読み上げモデルがない場合は無視
        if message.author.bot:
            return
        if message.content == "/leave" or "setup" in message.content:
            return
        if not self.listening and not self.pause:
            return
        if self.synthesizer is None:
            print(1)
            return
        if self.voice is None:
            return
        if message.channel.id != self.channel_id:
            print(2)
            return
        # 読み上げメッセージを50文字以内に短縮
        message_content = message.content
        if len(message_content) > 50:
            message_content = message_content[:50] + "以後略"

        # ランダムIDを振り、音声生成
        id = random.randint(0, 1000000)
        await self.make_audio(message_content, id)

        # 音声再生
        self.voice.play(discord.FFmpegPCMAudio(source=f"./temp/{id}.wav"))
        # 再生が終わるまで待機、終わり次第音声ファイル削除
        while self.voice.is_playing():
            await asyncio.sleep(1)
        os.remove(f"./temp/{id}.wav")

    # モデルを準備する
    async def make_model(self):
        # モデルセットアップに必要なパラメタを環境変数などから設定
        acceleration_mode = "CPU"
        vvm_dir = os.getenv("VVM_PATH")
        open_jtalk_dict_dir = os.getenv("OPEN_JTALK_DICT_DIR")

        # VoiceVoxのデフォルトスクリプトのコピペで、モデルをセットアップ
        logger.debug("%s", f"{voicevox_core.supported_devices()=}")

        logger.info(
            "%s", f"Initializing ({acceleration_mode=}, {open_jtalk_dict_dir=})"
        )
        synthesizer = Synthesizer(
            await OpenJtalk.new(open_jtalk_dict_dir),
            acceleration_mode=acceleration_mode,
        )
        logger.debug("%s", f"{synthesizer.metas=}")
        logger.debug("%s", f"{synthesizer.is_gpu_mode=}")
        # モデルの読み込みを必要なモノだけにして高速化
        # モデルはVVMをZIPにして確認可能
        files = os.listdir(vvm_dir)
        for files in files:
            if files.endswith(".vvm"):
                vvm_path = f"{vvm_dir}/{files}"
                logger.info("%s", f"Loading `{vvm_path}`")
                model = await VoiceModel.from_path(vvm_path)
                await synthesizer.load_voice_model(model)

        return synthesizer

    # テキストから音声生成
    async def make_audio(self, text, id):
        # テキストから音声生成に必要なパラメタを設定
        audio_query = await self.synthesizer.audio_query(text, self.style_id)
        audio_query.intonation_scale = 1.33
        audio_query.speed_scale = 1.2
        audio_query.post_phoneme_length = 0
        audio_query.pre_phoneme_length = 0

        # 音声生成
        wav = await self.synthesizer.synthesis(audio_query, self.style_id)
        out = Path(f"./temp/{id}.wav")
        out.write_bytes(wav)
        logger.info("%s", f"Wrote `{out}`")

    async def setup_model(self):
        self.synthesizer = await self.make_model()


# Cogを追加
async def setup(bot: commands.Bot):

    await bot.add_cog(VoiceCog(bot))
