from datetime import datetime, timedelta
import time

import pytz

from helpers import log, timezone_now
from managers.AlgorithmsManager import AlgorithmsManager
from managers.FormManager import FormManager
from managers.Manager import Manager
from managers.MedicineManager import MedicineManager
from models import Contract, Patient, Medicine, Reminder
from threading import Thread
from pytz import timezone


class TimetableManager(Manager):
    def __init__(self, medicine_manager, form_manager, reminder_manager, *args):
        super(TimetableManager, self).__init__(*args)
        self.medicine_manager = medicine_manager
        self.form_manager = form_manager
        self.reminder_manager = reminder_manager

    def should_run(self, object, today=False):
        now = timezone_now(object.contract.timezone)
        zone = pytz.timezone(object.contract.timezone)
        moscow_zone = pytz.timezone('Europe/Moscow')

        timetable = object.timetable

        if (isinstance(object, Medicine) or isinstance(object, Reminder)) and object.canceled_at is not None:
            return False

        if timetable.get('mode') == 'manual':
            return False

        if object.last_sent:
            last_sent = max(moscow_zone.localize(object.last_sent), now - timedelta(minutes=5))
        else:
            last_sent = now - timedelta(minutes=5)

        if isinstance(object, Reminder) and object.send_next:
            return now >= object.send_next > last_sent

        points = timetable['points']
        if timetable['mode'] == 'weekly':
            points = list(filter(lambda x: x['day'] == now.weekday(), points))
        if timetable['mode'] == 'monthly':
            points = list(filter(lambda x: x['day'] == now.day, points))

        if today:
            return bool(points)

        timepoints = list(
            map(lambda p:
                zone.localize(
                    datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month, year=now.year)
                ),
                points)
        )
        print(timepoints)

        return bool(list(filter(lambda p: p <= now and p > last_sent, timepoints)))

    def run_if_should(self, objects, manager):
        for object in objects:
            if object and self.should_run(object):
                manager.run(object)
                manager.log_request(object)

    def update_daily_tasks(self, app):
        print("Start tasks update")
        with app.app_context():

            contracts = list(Contract.query.filter_by(is_active=True).all())

            for contract in contracts:
                try:
                    daily_forms = list(filter(lambda f: self.should_run(f, True), contract.forms))
                    daily_medicines = list(filter(lambda m: self.should_run(m, True), contract.medicines))

                    if contract.tasks is not None:
                        for task_id in contract.tasks.values():
                            self.medsenger_api.delete_task(contract.id, task_id)

                    tasks = {}

                    for form in daily_forms:
                        task = self.medsenger_api.add_task(contract.id, form.title,
                                                           target_number=self.count_times(form),
                                                           action_link='form/{}'.format(form.id))
                        if task is not None:
                            tasks.update({'form-{}'.format(form.id): task['task_id']})

                    for medicine in daily_medicines:
                        task = self.medsenger_api.add_task(contract.id, medicine.title,
                                                           target_number=self.count_times(medicine),
                                                           action_link='medicine/{}'.format(medicine.id))
                        if task is not None:
                            tasks.update({'medicine-{}'.format(medicine.id): task['task_id']})

                    contract.tasks = tasks
                    self.__commit__()
                except Exception as e:
                    log(e, True)

    def count_times(self, obj):
        now = timezone_now(obj.contract.timezone)
        timetable = obj.timetable
        points = timetable['points']

        if timetable['mode'] == 'weekly':
            return len(list(filter(lambda x: x['day'] == now.weekday(), points)))
        if timetable['mode'] == 'monthly':
            return len(list(filter(lambda x: x['day'] == now.day, points)))

        return len(points)

    def check_hours(self, app):
        with app.app_context():
            contracts = list(Contract.query.filter_by(is_active=True).all())
            algorithm_groups = list(map(lambda x: x.algorithms, contracts))

            algorithm_manager = AlgorithmsManager(self.medsenger_api, self.db)

            for group in algorithm_groups:
                for alg in group:
                    if "exact_time" in alg.categories:
                        algorithm_manager.run(alg)

    def check_days(self, app):
        with app.app_context():
            contracts = list(Contract.query.filter_by(is_active=True).all())
            algorithm_groups = list(map(lambda x: x.algorithms, contracts))

            algorithm_manager = AlgorithmsManager(self.medsenger_api, self.db)

            for group in algorithm_groups:
                for alg in group:
                    if "exact_date" in alg.categories:
                        algorithm_manager.run(alg)

    def iterate(self, app):
        with app.app_context():
            contracts = list(Contract.query.filter_by(is_active=True).all())

            medicines_groups = list(map(lambda x: x.medicines, contracts))
            forms_groups = list(map(lambda x: x.forms, contracts))
            reminders_groups = list(map(lambda x: x.reminders, contracts))

            for medicines in medicines_groups:
                self.run_if_should(medicines, self.medicine_manager)

            for forms in forms_groups:
                self.run_if_should(forms, self.form_manager)

            for reminders in reminders_groups:
                self.run_if_should(reminders, self.reminder_manager)

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
