#!/bin/sh

killall -9 pyro4-ns
export PYRO_SERIALIZERS_ACCEPTED=pickle
export PYRO_SERIALIZER=pickle
pyro4-ns -n 0.0.0.0 -p 8001&
python Mojo.py
