set "path=%cd%"

START "elasticsearch" /D %path% "elasticsearch-1.7.5\bin\elasticsearch.bat"
rem START "redis" /D %path% "redis-2.4.5\redis-server.exe"
START "hunterInfo" /D %path% "Python27\python.exe" "hunterInfo\manage.py" "runserver" "localhost:80"

Python27\python.exe backup.py
