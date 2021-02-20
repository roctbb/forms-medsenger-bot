from datetime import datetime, timedelta
import time
from helpers import log
from managers.Manager import Manager
from models import Contract
from threading import Thread


class TimetableManager(Manager):
    def __init__(self, medicine_manager, form_manager, *args):
        super(TimetableManager, self).__init__(*args)
        self.medicine_manager = medicine_manager
        self.form_manager = form_manager

    def should_run(self, object):
        now = datetime.now()
        timetable = object.timetable
        last_sent = max(object.last_sent, now - timedelta(minutes=5))

        points = self.get_timepoints(timetable)

        return bool(list(filter(lambda x: x <= now and x >= last_sent, points)))

    def run_if_should(self, objects):
        for object in objects:
            if self.should_run(object):
                object.run()

    def iterate(self):
        contracts = Contract.query.filter_by(is_active=True).all()

        medicines = list(map(lambda x: x.medicines, contracts))
        forms = list(map(lambda x: x.forms, contracts))

        self.run_if_should(medicines)
        self.run_if_should(forms)

    def worker(self, app):
        while True:
            with app.app_context():
                self.iterate()
                time.sleep(60)

    def run(self, app):
        thread = Thread(target=self.worker, args=[app, ])
        thread.run()
