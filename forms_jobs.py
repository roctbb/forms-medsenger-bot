from forms_bot import *
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(timetable_manager.iterate, 'interval', minutes=1, args=(app, ))
scheduler.add_job(timetable_manager.check_forgotten, 'interval', days=1, args=(app, ))
scheduler.add_job(timetable_manager.check_hours, 'interval', hours=1, args=(app, ))
scheduler.start()



