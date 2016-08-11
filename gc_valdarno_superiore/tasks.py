from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.signals import after_task_publish,task_success,task_prerun,task_postrun, before_task_publish
from prova_lamma.emails import send_feedback_email

logger = get_task_logger(__name__)

@task(name="send_feedback_email_task")
def send_feedback_email_task(email, codice_segnalazione):
    """sends an email when feedback form is filled successfully"""
    logger.info("Sent feedback email")
    return send_feedback_email(email, codice_segnalazione)
    
@task_postrun.connect()
def task_postrun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None):
    # note that this hook runs even when there has been an exception thrown by the task
    logger.info("Sent feedback email POST RUN")
    print "post run {0} ".format(task)
    
@task_prerun.connect()
def task_prerun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None):
    logger.info("Sent feedback email PRE RUN")
    if task.name =="send_feedback_email_task":
        print "pre-run of add. Do special add things here. Task: {0}  sender: {1}".format(task,sender)