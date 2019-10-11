@echo off

set PY=python
if exist ..\LaF\py.cmd (set PY=..\LaF\py.cmd)
%PY% MojoLock.py