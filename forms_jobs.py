from forms_bot import *
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(timetable_manager.iterate, 'interval', minutes=5, args=(app, ))
scheduler.start()
