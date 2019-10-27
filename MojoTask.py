from Mojo import Mojo
import Task

import Pyro4
@Pyro4.expose    
class MojoTask(Task.Task):
    def __init__(self, mojo=None):
        Task.Task.__init__(self)
        self.mojo = mojo or Mojo()
     
    def ports(self):
        return self.mojo.ports()
        
    def open(self, port):
        return self.mojo.open(port)
        
    def close(self):
        return self.mojo.close()
    
    def load(self, path):
        return self.mojo.load(path)
        
    @Task.task
    def write(self, *args, **kwargs):
        return self.mojo.write(*args, **kwargs)
    
    @Task.task
    def read(self, *args, **kwargs):
        return self.mojo.read(*args, **kwargs)

if __name__ == '__main__':    
    #HOST = '127.0.0.1'
    HOST = '192.168.1.2'
    Pyro4.config.SERIALIZER = 'pickle'
    Pyro4.SERIALIZERS_ACCEPTED = 'pickle'
    daemon = Pyro4.Daemon(HOST,8000)            
    ns = Pyro4.locateNS()                  
    uri = daemon.register(MojoTask())
    ns.register("mojo", uri) 
    daemon.requestLoop()