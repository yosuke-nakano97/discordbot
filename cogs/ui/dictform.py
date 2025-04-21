from discord import ui
import discord


class DictForm(ui.Modal):
    def __init__(self, feature):
        super().__init__(
            title="カスタム辞書",
            timeout=None,
        )
        self.feature = feature
        self.word = discord.ui.TextInput(
            label="メッセージ",
            style=discord.TextStyle.short,
            placeholder="Input message here",
            default=("ここに単語をいれてね"),
            required=True,
            max_length=30,
        )
        self.pros = discord.ui.TextInput(
            label="よみ（カタカナオンリーで）",
            required=True,
            default=("ここに読みいれてね"),
        )
        self.add_item(self.word)
        self.add_item(self.pros)

    async def on_submit(self, interaction: discord.Interaction):

        if not all("\u30a1" <= char <= "\u30fc" for char in self.pros.value):
            await interaction.response.send_message(
                "よみはカタカナのみで入力してください", ephemeral=True
            )
            self.stop()
            self.feature.set_result([0, 0])
            return

        await interaction.response.send_message(
            f"たんご: {self.word.value}\nよみ: {self.pros.value}"
        )
        self.stop()
        self.feature.set_result([self.word.value, self.pros.value])
