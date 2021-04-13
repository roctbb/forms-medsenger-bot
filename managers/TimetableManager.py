from datetime import datetime, timedelta
import time
from helpers import log
from managers.AlgorithmsManager import AlgorithmsManager
from managers.FormManager import FormManager
from managers.Manager import Manager
from managers.MedicineManager import MedicineManager
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

        points = list(map(lambda p: datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month, year=now.year), points))

        return bool(list(filter(lambda p: p <= now and p > last_sent, points)))

    def run_if_should(self, objects, manager):
        for object in objects:
            if object and self.should_run(object):
                manager.run(object)

    def check_hours(self, app):
        with app.app_context():
            contracts = list(Contract.query.filter_by(is_active=True).all())
            algorithm_groups = list(map(lambda x: x.algorithms, contracts))

            algorithm_manager = AlgorithmsManager(self.medsenger_api, self.db)

            for group in algorithm_groups:
                for alg in group:
                    if "exact_time" in alg.categories:
                        algorithm_manager.run(alg)

    def iterate(self, app):
        with app.app_context():
            contracts = list(Contract.query.filter_by(is_active=True).all())

            medicines_groups = list(map(lambda x: x.medicines, contracts))
            forms_groups = list(map(lambda x: x.forms, contracts))

            for medicines in medicines_groups:
                self.run_if_should(medicines, self.medicine_manager)

            for forms in forms_groups:
                self.run_if_should(forms, self.form_manager)

    def check_forgotten(self, app):
        with app.app_context():
            contracts = list(Contract.query.filter_by(is_active=True).all())
            medicine_manager = MedicineManager(self.medsenger_api, self.db)
            form_manager = FormManager(self.medsenger_api, self.db)

            medicines_groups = list(map(lambda x: x.medicines, contracts))
            forms_groups = list(map(lambda x: x.forms, contracts))

            for medicines in medicines_groups:
                for medicine in medicines:
                    medicine_manager.check_warning(medicine)

            for forms in forms_groups:
                for form in forms:
                    form_manager.check_warning(form)

    def worker(self, app):
        while True:
            self.iterate(app)
            self.check_forgotten(app)
            time.sleep(60)


    def run(self, app):
        thread = Thread(target=self.worker, args=[app, ])
        thread.start()
