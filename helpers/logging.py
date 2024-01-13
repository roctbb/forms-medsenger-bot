
from config import *
from .timing import *
from sentry_sdk import capture_exception
import traceback
import os
import sys

def log(error, terminating=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    if PRODUCTION:
        capture_exception(error)

    if terminating:
        print(traceback.format_exc())
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error, "CRITICAL")
    else:
        print(traceback.format_exc())
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error)