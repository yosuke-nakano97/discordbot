from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from vken import bot


# APSchedulerを操作するクラス
class Schedule:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    # 予約を追加する
    def add_job(self, date, id):
        # Cogの関数と予約をれんけい
        mycog = bot.get_cog("BookingCog")
        trigger = DateTrigger(run_date=date)
        job = self.scheduler.add_job(func=mycog.remind, trigger=trigger, args=[id])
        return job

    # すべての予約を取得する
    def get_jobs(self):
        return self.scheduler.get_jobs()

    def delete_job(self, id):
        self.scheduler.remove_job(id)


schedule = Schedule()
