from app import celery_app
from celery import task
from data_processor import prepare, post_prepare

@celery_app.task()
def file_processor(sessionID, target, sa_filename):
    try:
        print("Yes Working")
        prepare(sessionID, target, sa_filename)
    except IOError as e:
        logging.error("Input Error %s" % (str(e)))