from datetime import datetime, timedelta
import time
from helpers import log
from managers.Manager import Manager
from models import Contract, Patient
from threading import Thread


class TimetableManager(Manager):
    def __init__(self, medicine_manager, form_manager, *args):
        super(TimetableManager, self).__init__(*args)
        self.medicine_manager = medicine_manager
        self.form_manager = form_manager

    def should_run(self, object):
        now = datetime.now()
        timetable = object.timetable
        if object.last_sent:
            last_sent = max(object.last_sent, now - timedelta(minutes=5))
        else:
            last_sent = now - timedelta(minutes=5)

        points = timetable['points']
        if timetable['mode'] == 'weekly':
            points = list(filter(lambda x:x['day'] == now.weekday(), points))
        if timetable['mode'] == 'montly':
            points = list(filter(lambda x: x['day'] == now.weekday(), points))

        points = list(map(lambda p: datetime(minute=p['minute'], hour=p['hour'], day=now.day, month=now.month, year=now.year), points))

        return bool(list(filter(lambda p: p <= now and p > last_sent, points)))

    def run_if_should(self, objects, manager):
        for object in objects:
            if object and self.should_run(object):
                manager.run(object)

    def iterate(self):
        contracts = list(Contract.query.filter_by(is_active=True).all())

        medicines_groups = list(map(lambda x: x.medicines, contracts))
        forms_groups = list(map(lambda x: x.forms, contracts))

        for medicines in medicines_groups:
            self.run_if_should(medicines, self.medicine_manager)

        for forms in forms_groups:
            self.run_if_should(forms, self.form_manager)

    def worker(self, app):
        while True:
            with app.app_context():
                self.iterate()
            time.sleep(60)

    def run(self, app):
        thread = Thread(target=self.worker, args=[app, ])
        thread.start()
