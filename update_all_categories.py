from manage import *
from models import *

with app.app_context():
    for algorithm in Algorithm.query.all():
        algorithm_manager.update_categories(algorithm)
    db.session.commit()