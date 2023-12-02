from manage import *
from tasks import *
import os

dates = ['2023-11-22', '2023-11-23', '2023-11-24', '2023-11-24', '2023-11-24', '2023-11-24', '2023-11-24', '2023-11-24',
         '2023-11-25', '2023-11-26', '2023-11-27', '2023-11-28', '2023-11-29', '2023-11-30', '2023-12-01', '2023-11-02']
os.environ['DRY_RUN'] = 'true'

for date in dates:
    os.environ['EMULATED_DATE'] = date
    timetable_manager.check_days(app)
