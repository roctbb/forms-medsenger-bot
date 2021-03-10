from forms_bot import *
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(timetable_manager.iterate(app), 'interval', minutes=5)
scheduler.start()
