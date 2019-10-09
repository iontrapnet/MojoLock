import sys
from threading import Thread, Lock, Event
from functools import wraps

PY3 = sys.version_info[0] == 3

if PY3:
    from queue import Queue
else:
    from Queue import Queue

def task(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        name = '_'+func.__name__
        if not getattr(self.__class__, name, None): setattr(self.__class__,name,func)
        id = kwargs.get('id', '')
        self._task.put((name, str(id))+args)
    return wrapper
    
class Task:
    def __init__(self):
        self._task = Queue()
        self._last = {}
        self._lock = Lock()
        self._quit = Event()
        self._worker = Thread(target=self._run)
        self._worker.setDaemon(True)
        self._worker.start()
        
    def _run(self):
        while not self._quit.is_set():
            call = self._task.get()
            result = getattr(self, call[0])(*call[2:])
            with self._lock:
                self._last[call[0]+call[1]] = result
            self._task.task_done()
    
    def wait(self, timeout = 0):
        self._quit.wait(timeout)
    
    def quit(self):
        self._quit.set()
        
    def __getitem__(self, item):
        with self._lock:
            return self._last.get('_'+item)