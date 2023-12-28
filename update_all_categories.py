from manage import *
from models import *

with app.app_context():
    for algorithm in Algorithm.query.all():
        try:
            algorithm_manager.update_categories(algorithm)
        except Exception as e:
            print("Problem with algorithm {}: {}".format(algorithm.id, e))
    db.session.commit()