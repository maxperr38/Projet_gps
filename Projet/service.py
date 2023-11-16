from spyne import Application, rpc, ServiceBase, Unicode, Float, Integer, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import math


class HelloWorldService(ServiceBase):
  
    #@rpc(Unicode, Integer, _returns=Iterable(Unicode))
    #def say_hello(ctx, name, times):
     #   for i in range(times):
     #       yield u'Hello, %s' % name
    #@rpc(Integer, Integer, _returns=Integer)
    #def addition(ctx, a, b):
    #    return a + b

    @rpc(Float, Float, Float, Float, _returns=Unicode)
    def temps(ctx, d, v, autonomie, temps_charge):
        nb_recharge = math.ceil(d / autonomie)
        distance = d * 1000  # convertir en mètres
        vitesse = v * 1000 / 3600  # convertir en mètres par seconde
        timeseconde = (distance / vitesse)  # calculer le temps en secondes
        if nb_recharge >= 1:
            temps_supp = temps_charge * 60 * nb_recharge
        else:
            temps_supp = 0
        
        timeseconde = timeseconde + temps_supp    
        
        
        hours = int(timeseconde // 3600)
        minutes = int((timeseconde % 3600) // 60)
        seconds = int(timeseconde % 60)
        
        return f"{hours}h {minutes}m {seconds}s"

application = Application(
    [HelloWorldService],
    'spyne.examples.hello.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('192.168.141.59', 8000, wsgi_application)
    print("listening to http://192.168.141.59:8000")
    print("wsdl is at: http://192.168.141.59:8000/?wsdl")

    
    server.serve_forever()
