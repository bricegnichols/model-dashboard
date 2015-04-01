from celery import Celery
import os
from celery.utils.log import get_task_logger

app = Celery('tasks', backend='amqp', broker='amqp://psrc:psrc1@10.10.11.89/psrcvhost')

@app.task
def add(x, y):
	logger.info('Adding %s + %s' % (x, y))
    return x + y

@app.task
def mul(x, y):
    return x * y

@app.task
def xsum(numbers):
    return sum(numbers)

@app.task
def make_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)