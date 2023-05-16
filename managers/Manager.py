import pytz
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from medsenger_api import AgentApiClient

from helpers import timezone_now, localize
from models import ActionRequest


class Manager:
    def __init__(self, medsenger_api: AgentApiClient, db: SQLAlchemy):
        self.medsenger_api = medsenger_api
        self.db = db

    def __commit__(self):
        self.db.session.commit()

    def get_timepoints(self, timetable, zone=None):
        now = timezone_now(zone)
        raw = timetable['points']
        points = []

        if timetable['mode'] == 'daily':
            points = list(
                map(lambda p: localize(datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month,
                                       year=now.year), zone), raw))
            points.sort()
            if points:
                points.append(points[0] + timedelta(days=1))
        if timetable['mode'] == 'weekly':
            current_weekday_points = list(filter(lambda x: x['day'] == now.weekday(), raw))
            current_weekday_points = list(
                map(lambda p: localize(datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month,
                                       year=now.year), zone), current_weekday_points))

            next_points = []
            for i in range(1, 8):
                next_points = list(filter(lambda x: x['day'] == (now.weekday() + i) % 7, raw))

                if next_points:
                    break

            next_points = list(
                map(lambda p: localize(datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month,
                                       year=now.year), zone) + timedelta(days=i), next_points))

            points = current_weekday_points + next_points
            points.sort()

        if timetable['mode'] == 'monthly':
            points = list(
                map(lambda p: localize(datetime(minute=int(p['minute']), hour=int(p['hour']), day=int(p['day']), month=now.month,
                                       year=now.year), zone), raw))
            points.sort()
            if points:
                try:
                    year = now.year if points[0].month + 1 <= 12 else now.year + 1
                    month = 1 if points[0].month == 12 else points[0].month + 1
                    points.append(
                            localize(datetime(minute=points[0].minute, hour=points[0].hour, day=points[0].day, month=month,
                                 year=year), zone))
                except:
                    pass
        return points

    def calculate_deadline(self, obj):
        zone = None

        if obj.contract:
            zone = obj.contract.get_actual_timezone()

        if obj.timetable.get('mode') == 'manual':
            return None

        now = timezone_now(zone)
        points = self.get_timepoints(obj.timetable, zone)

        if points:
            greater = next(filter(lambda x: x > now, points))
        else:
            return None

        return int(greater.timestamp() - 1)

    def get_templates(self):
        return []

    def get_templates_as_dicts(self):
        return [template.as_dict() for template in self.get_templates()]

    def log_request(self, action, contract_id=None, description=None):
        self.db.session.add(
            ActionRequest(contract_id=contract_id, action=action, description=description))
        self.__commit__()

    def log_done(self, action, contract_id):
        record = ActionRequest.query.filter_by(contract_id=contract_id, action=action).order_by(
            ActionRequest.id.desc()).first()

        if record and not record.is_done:
            record.is_done = True
            record.done = datetime.now()
            self.__commit__()

