from src import start, make_celery

app = start()
celery = make_celery(app)
