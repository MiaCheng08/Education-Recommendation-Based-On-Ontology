
"""

from apscheduler.schedulers.blocking import BlockingScheduler
def my_job():
    print('hello world')

sched = BlockingScheduler()
sched.add_job(my_job, 'interval', seconds=1)
sched.start()
"""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

def tick():
    print('Tick! The time is: %s' % datetime.now())


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=1)
    print('Press Ctrl+C to exit')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
