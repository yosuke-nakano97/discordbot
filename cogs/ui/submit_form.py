from discord import ui
from util.schedule import schedule
import discord
import datetime
from database import dbmanage


class EditSubmitForm(ui.Modal):
    def __init__(self, booking):
        self.add_item(self.message)
        self.date = discord.ui.TextInput(
            label="予約日(DDとHHの間のスペースは必須‼‼)",
            required=True,
            placeholder="YYYY-MM-DD HH:MM",
            default=booking.datetime.strftime("%Y-%m-%d %H:%M"),
        )
        self.add_item(self.date)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.booking.message = self.message.value
            dateinfo = datetime.datetime.strptime(self.date.value, "%Y-%m-%d %H:%M")
            self.booking.datetime = dateinfo
            dbmanage.Dbmanage().update_booking(self.booking)
        except Exception as e:
            await interaction.response.send_message(
                "日時がおかしいかも！", view=EditTimecheck(self.booking), ephemeral=True
            )
            print(e)
            return
        channel_name = interaction.channel.name
        if self.booking.target is not None:
            if self.booking.role:
                rolename = interaction.guild.get_role(self.booking.target).name
            else:
                rolename = interaction.guild.get_member(self.booking.target).name
        else:
            rolename = None
        await interaction.response.send_message(
            f"channel:{channel_name}\ntarget:{rolename}\ndatetime:{self.booking.datetime}\ncontent:{self.booking.message}",
            ephemeral=True,
        )
        schedule.delete_job(self.booking.job_id)

        self.booking.job_id = schedule.add_job(
            date=self.booking.datetime, id=self.booking.id
        ).id
        update = dbmanage.Dbmanage().update_booking(self.booking)


class SubmitForm(ui.Modal):
    def __init__(self, booking):
        super().__init__(
            title="予約投稿フォーム",
            timeout=None,
        )
        self.booking = booking
        self.message = discord.ui.TextInput(
            label="メッセージ",
            style=discord.TextStyle.long,
            placeholder="Input message here",
            default=(self.booking.message or "ここに本文いれてネ"),
            required=True,
            max_length=300,
        )
        self.date_default = "YYYY-MM-DD HH:MM"
        if self.booking.datetime:
            self.date_default = self.booking.datetime.strftime("%Y-%m-%d %H:%M")
        self.date = discord.ui.TextInput(
            label="予約日(DDとHHの間のスペースは必須‼‼)",
            required=True,
            placeholder="YYYY-MM-DD HH:MM",
            default=self.date_default,
        )
        self.add_item(self.message)
        self.add_item(self.date)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.booking.message = self.message.value
            dateinfo = datetime.datetime.strptime(self.date.value, "%Y-%m-%d %H:%M")
            self.booking.datetime = dateinfo
            today = datetime.datetime.now()
            if dateinfo < today:
                raise ValueError("The date cannot be in the past.")
            if dateinfo > today + datetime.timedelta(days=60):
                await interaction.response.send_message(
                    "2か月以内にしてほしいゴマ！",
                    view=Timecheck(self.booking),
                    ephemeral=True,
                )
                return
            dbmanage.Dbmanage().reg_booking(self.booking)
        except Exception as e:
            await interaction.response.send_message(
                "日時がおかしいかも！", view=Timecheck(self.booking), ephemeral=True
            )
            print(e)
            return
        channel_name = interaction.channel.name
        if self.booking.target is not None:
            if self.booking.role:
                rolename = interaction.guild.get_role(self.booking.target).name
            else:
                rolename = interaction.guild.get_member(self.booking.target).name
        else:
            rolename = None
        await interaction.response.send_message(
            f"channel:{channel_name}\ntarget:{rolename}\ndatetime:{self.booking.datetime}\ncontent:{self.booking.message}",
            ephemeral=True,
        )
        self.booking.job_id = schedule.add_job(
            date=self.booking.datetime, id=self.booking.id
        ).id
        dbmanage.Dbmanage().update_booking(self.booking)


class MentionSelectView(ui.View):
    def __init__(self, booking):
        super().__init__(timeout=30)
        self.add_item(MentionSelect(booking))


class MentionSelect(ui.MentionableSelect):
    def __init__(self, booking):
        self.booking = booking
        super().__init__(
            placeholder="メンションを送信するユーザー,ロールを選択してください",
            min_values=0,
            max_values=1,
        )

    async def callback(self, interaction):
        self.booking.target = self.values[0].id if self.values else None
        if type(self.values[0]) is discord.Role:
            self.booking.role = True
        else:
            self.booking.role = False

        await interaction.response.edit_message(
            content="予約中", view=None, delete_after=0.1
        )

        await interaction.followup.send(
            content="ごめん！これ押して‼‼",
            view=Temp(booking=self.booking),
            ephemeral=True,
        )


class ChannelSelectView(ui.View):
    def __init__(self, booking):
        super().__init__(timeout=30)
        self.add_item(ChannelSelect(booking))


class ChannelSelect(ui.ChannelSelect):
    def __init__(self, booking):
        self.booking = booking
        super().__init__(
            placeholder="メッセージを送信するチャンネルを選択してください",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
        )

    async def callback(self, interaction: discord.Interaction):
        self.booking.channel_id = self.values[0].id
        view = MentionSelectView(self.booking)
        await interaction.response.edit_message(
            content="メンションしたい人、ロール選んでネ", view=view
        )


class Temp(discord.ui.View):
    def __init__(self, booking):
        super().__init__()
        self.booking = booking

    @discord.ui.button(label="続ける", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(SubmitForm(booking=self.booking))
        self.stop()


class Timecheck(discord.ui.View):
    def __init__(self, booking):
        super().__init__()
        self.booking = booking

    @discord.ui.button(label="続ける", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(SubmitForm(booking=self.booking))
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class BookingSelectView(ui.View):
    def __init__(self, bookings):
        super().__init__(timeout=30)
        self.add_item(BookingSelect(bookings))


class BookingSelect(ui.Select):
    def __init__(self, bookings):
        self.bookings = bookings
        options = [
            discord.SelectOption(
                label=f"id:{booking.id},date:{booking.datetime}",
                value=booking.id,
            )
            for booking in bookings
        ]
        super().__init__(
            placeholder="予約を選択してください",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction):
        for i in range(len(self.bookings)):
            if self.bookings[i].id == int(self.values[0]):
                booking_index = i
                break
        await interaction.response.edit_message(
            content=f"チャンネル選んでネ",
            view=EditChannelSelectView(self.bookings[booking_index]),
        )


class EditChannelSelectView(ui.View):
    def __init__(self, booking):
        super().__init__(timeout=30)
        self.add_item(EditChannelSelect(booking))


class EditChannelSelect(ui.ChannelSelect):
    def __init__(self, booking):
        self.booking = booking

        super().__init__(
            placeholder="メッセージを送信するチャンネルを選択してネ",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
        )

    async def callback(self, interaction: discord.Interaction):
        self.booking.channel_id = self.values[0].id
        view = EditMentionSelectView(self.booking)
        await interaction.response.edit_message(
            content="メンションしたい人、ロール選んでネ", view=view
        )


class EditMentionSelectView(ui.View):
    def __init__(self, booking):
        super().__init__(timeout=30)
        self.add_item(EditMentionSelect(booking))


class EditMentionSelect(ui.MentionableSelect):
    def __init__(self, booking):
        self.booking = booking
        super().__init__(
            placeholder="メンションを送信するユーザー,ロールを選択してネ",
            min_values=0,
            max_values=1,
        )

    async def callback(self, interaction):
        self.booking.target = self.values[0].id if self.values else None
        if type(self.values[0]) is discord.Role:
            self.booking.role = True
        else:
            self.booking.role = False

        await interaction.response.edit_message(
            content="予約中", view=None, delete_after=0.1
        )

        await interaction.followup.send(
            content="ごめん！これ押して‼‼",
            view=EditTemp(booking=self.booking),
            ephemeral=True,
        )


class EditTemp(discord.ui.View):
    def __init__(self, booking):
        super().__init__()
        self.booking = booking

    @discord.ui.button(label="続ける", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(EditSubmitForm(booking=self.booking))
        self.stop()


class EditSubmitForm(ui.Modal):
    def __init__(self, booking):
        super().__init__(
            title="予約投稿フォーム",
            timeout=None,
        )
        self.booking = booking
        self.date_default = booking.datetime or "YYYY-MM-DD HH:MM"
        self.message = discord.ui.TextInput(
            label="メッセージ",
            style=discord.TextStyle.long,
            placeholder="Input message here",
            default=booking.message,
            required=True,
            max_length=300,
        )
        self.add_item(self.message)
        self.date = discord.ui.TextInput(
            label="予約日(DDとHHの間のスペースは必須‼‼)",
            required=True,
            placeholder="YYYY-MM-DD HH:MM",
            default=booking.datetime.strftime("%Y-%m-%d %H:%M"),
        )
        self.add_item(self.date)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.booking.message = self.message.value
            dateinfo = datetime.datetime.strptime(self.date.value, "%Y-%m-%d %H:%M")
            self.booking.datetime = dateinfo
            dbmanage.Dbmanage().update_booking(self.booking)
        except Exception as e:
            await interaction.response.send_message(
                "日時がおかしいかも！", view=EditTimecheck(self.booking), ephemeral=True
            )
            print(e)
            return
        channel_name = interaction.channel.name
        if self.booking.target is not None:
            if self.booking.role:
                rolename = interaction.guild.get_role(self.booking.target).name
            else:
                rolename = interaction.guild.get_member(self.booking.target).name
        else:
            rolename = None
        await interaction.response.send_message(
            f"channel:{channel_name}\ntarget:{rolename}\ndatetime:{self.booking.datetime}\ncontent:{self.booking.message}",
            ephemeral=True,
        )
        schedule.delete_job(self.booking.job_id)

        self.booking.job_id = schedule.add_job(
            date=self.booking.datetime, id=self.booking.id
        ).id
        update = dbmanage.Dbmanage().update_booking(self.booking)


class EditTimecheck(discord.ui.View):
    def __init__(self, booking):
        super().__init__()
        self.booking = booking

    @discord.ui.button(label="続ける", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(EditSubmitForm(booking=self.booking))
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()
