import logging, logging, os, discord, re, random, cv2
from database.dbmanage import Dbmanage
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import numpy as np
from database.dbmanage import Dbmanage
import shutil

# ロガーの設定
logger = logging.getLogger(__name__)


class QuizCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mosaic")
    async def mosic(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(ephemeral=True, thinking=True)
        base_dir = f"images/{interaction.user.name}"
        counter = 1
        save_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        save_dir = f"{base_dir}/{len(os.listdir(base_dir))}"
        image_path = f"{save_dir}/input.png"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        await image.save(image_path)
        answer = f"{save_dir}/answer"
        os.makedirs(answer, exist_ok=True)
        answer_file_path = f"{answer}/{image.filename}"
        with open(answer_file_path, 'w') as f:
            pass
        try:
            for i in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
                output_path = f"{save_dir}/mosaic_{i}.png"
                self.apply_solo_mosaic(image_path, output_path, i, i)
            await interaction.followup.send(
                ephemeral=True,
                content="モザイク処理が完了したよ！",
            )
            # ディレクトリを圧縮
            zip_path = f"{save_dir}.zip"
            shutil.make_archive(save_dir, 'zip', save_dir)
            shutil.rmtree(save_dir, ignore_errors=True)

        except Exception as e:
            await interaction.followup.send(ephemeral=True, content=f"モザイク処理中にエラー発生しちゃった！もう一回お願い！")
            return

    @app_commands.command(name="shadow")
    async def shadow(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(ephemeral=True, thinking=True)
        save_dir = f"images/shadow/{interaction.user.id}/{image.filename.split('.')[0].split('_')[0]}"
        image_path = f"{save_dir}/input.png"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        await image.save(image_path)
        

    def apply_solo_mosaic(self, image_path, output_path, width, height ):
        # 画像を読み込む
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if image is None:
            print("画像が読み込めませんでした。パスを確認してください。")
            raise Exception()

        # 元のサイズを取得
        ori_height, ori_width = image.shape[:2]

        # 縮小してから拡大（モザイクの基本的な手法）
        small = cv2.resize(image, (width,height), interpolation=cv2.INTER_LINEAR)
        mosaic = cv2.resize(small, (ori_width, ori_height), interpolation=cv2.INTER_NEAREST)

        # 保存
        cv2.imwrite(output_path, mosaic)
        

    def blacken_foreground(input_path, output_path):
        # 画像読み込み
        img = cv2.imread(input_path)
        if img is None:
            print("画像が読み込めませんでした")
            return

        # 背景が単色前提 → 左上ピクセルを背景と仮定
        background_color = img[0, 0]

        # 背景と似てるピクセルをマスク（許容差あり）
        lower = np.array(background_color - 10)
        upper = np.array(background_color + 10)
        mask = cv2.inRange(img, lower, upper)

        # 背景はそのまま、キャラ部分は黒
        result = img.copy()
        result[mask == 0] = [0, 0, 0]  # 黒で塗る

        # 保存
        cv2.imwrite(output_path, result)
        print(f"保存しました: {output_path}")


async def setup(bot: commands.Bot):

    await bot.add_cog(QuizCog(bot))