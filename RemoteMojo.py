from MojoTask import MojoTask
import rpyc

#HOST = '127.0.0.1'
HOST = '192.168.1.2'

#PATH = 'C:\\iontrapnet\\MojoLock'
PATH = '/home/tiqs/iontrapnet/MojoLock'

if True:
    _conn = rpyc.classic.connect(HOST, 8000)
    _conn.modules.sys.path.append(PATH)
    _conn.execute('import Mojo')
    Mojo = _conn.modules.Mojo.Mojo
    mojo = Mojo()
else:
    import Pyro4
    Pyro4.config.SERIALIZER = 'pickle'
    Pyro4.SERIALIZERS_ACCEPTED = 'pickle'
    mojo = Pyro4.Proxy('PYRONAME:mojo@' + HOST + ':8001')
    
    #import zerorpc
    #conn = zerorpc.Client()
    #conn.connect('tcp://127.0.0.1:8000')
    #mojo = conn

mojo_task = MojoTask(mojo)