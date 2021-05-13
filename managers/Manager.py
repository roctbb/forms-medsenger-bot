from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from medsenger_api import AgentApiClient


class Manager:
    def __init__(self, medsenger_api: AgentApiClient, db: SQLAlchemy):
        self.medsenger_api = medsenger_api
        self.db = db

    def __commit__(self):
        self.db.session.commit()

    def get_timepoints(self, timetable):
        now = datetime.now()
        raw = timetable['points']
        points = []

        if timetable['mode'] == 'daily':
            points = list(map(lambda p: datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month, year=now.year), raw))
            points.sort()
            if points:
                points.append(points[0] + timedelta(days=1))
        if timetable['mode'] == 'weekly':
            current_weekday_points = list(filter(lambda x: x['day'] == now.weekday(), raw))
            current_weekday_points = list(map(lambda p: datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month, year=now.year), current_weekday_points))

            next_points = []
            for i in range(1, 8):
                next_points = list(filter(lambda x: x['day'] == (now.weekday() + i) % 7, raw))

                if next_points:
                    break

            next_points = list(map(lambda p: datetime(minute=int(p['minute']), hour=int(p['hour']), day=now.day, month=now.month, year=now.year) + timedelta(days=i), next_points))

            points = current_weekday_points + next_points
            points.sort()

        if timetable['mode'] == 'monthly':
            points = list(map(lambda p: datetime(minute=int(p['minute']), hour=int(p['hour']), day=int(p['day']), month=now.month, year=now.year), raw))
            points.sort()
            if points:
                points.append(datetime(minute=points[0].minute, hour=points[0].hour, day=points[0].day, month=points[0].month + 1, year=now.year))
        return points

    def calculate_deadline(self, timetable):
        now = datetime.now()

        points = self.get_timepoints(timetable)
        greater = list(filter(lambda x: x > now, points))[0]

        return int(greater.timestamp() - 1)

    def get_templates(self):
        return []

    def get_templates_as_dicts(self):
        return [template.as_dict() for template in self.get_templates()]
