@echo off

taskkill /im pyro4-ns.exe
set PYRO_SERIALIZERS_ACCEPTED=pickle
set PYRO_SERIALIZER=pickle
start pyro4-ns -n 0.0.0.0 -p 8001
python Mojo.py
