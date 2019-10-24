#!/bin/sh

killall -9 pyro4-ns
export PYRO_SERIALIZERS_ACCEPTED=pickle
export PYRO_SERIALIZER=pickle
pyro4-ns -n 192.168.1.2 -p 8001&
python Mojo.py
