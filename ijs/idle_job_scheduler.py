
from ctypes import Structure, windll, c_uint, sizeof, byref
import time


class LastInputInfo(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


class scheduler():
    """
    Schedule definition. Jobs will run on 'days' if local time is the time range defined by hours and minutes
    """
    def __init__(self, days=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                 hour_start=0, hour_end=23, minute_start=0, minute_end=59):
        self.days = days
        self.hour_start = hour_start
        self.hour_end = hour_end
        self.minute_start = minute_start
        self.minute_end = minute_end
    


def get_idle_duration():
    """
    Returns idle time in seconds
    """
    lastInputInfo = LastInputInfo()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0




class idle_job_scheduler(object):

    def __init__(self, min_idle_time=300, schedule=scheduler()):
        """

        Parameters
        ----------
        min_idle_time: Integer
            Minimum required idle time in seconds
        schedule: Scheduler object
            Schedule definition
        """
        self.min_idle_time = min_idle_time
        self.schedule = schedule
        

    def __call__(self, fn, *args, **kwargs):
        def wrapper(*args, **kwargs):
            idle_time = get_idle_duration()
            if idle_time >= self.min_idle_time :
                time_now = time.localtime()
                day, hour, minute = time.strftime("%a:%H:%M", time_now).split(sep=':')
                hour = int(hour)
                minute = int(minute)
                if (
                    (self.schedule.hour_start <= hour <=self.schedule.hour_end) &
                    (self.schedule.minute_start <= minute <=self.schedule.minute_end)
                   ):
                    print('Starting job: %s. System was idle for %.2f seconds.' % (time.strftime('%a, %d %b %Y %H:%M:%S', time_now), idle_time) )
                    return fn(*args, **kwargs)
        return wrapper


if __name__ == '__main__':
    
    sch = scheduler()
    
    
    @idle_job_scheduler(0.5, sch)
    def test(i):
        return 1    
        
    n_seconds = 10
    counter=0
    for i in range(n_seconds):
        time.sleep(1)
        if test(i) is not None:
            counter = counter +1
    print('Test ran %d times in %d seconds.' % (counter, n_seconds))