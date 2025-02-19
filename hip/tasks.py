from celery import shared_task
import time

@shared_task
def process_large_calculation(x, y):

    time.sleep(5)  
    return x + y
