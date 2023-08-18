@echo off
setlocal

@REM ###################################################
@REM ######   Copyright (c) 2022-2023 pgEdge    ########
@REM ###################################################

set MY_HOME=%~sdp0

if "%MY_HOME%"=="%MY_HOME: =%" goto pgc_run
(
    echo The DOS Short Path is not enabled on this drive/directory.
    echo Your local System Administrator needs to fix before using BigSQL PGC from here.
    goto pgc_exit
)

:pgc_run

set MY_HOME=%MY_HOME:~0,-1%
set MY_LOGS=%MY_HOME%\logs\pgcli_log.out

cd /d %MY_HOME%
set PATH=%SYSTEMROOT%\System32;%SYSTEMROOT%\System32\wbem;"%PATH%"

if NOT EXIST "%MY_HOME%\hub_new" goto pgc_cmd
(
   rename hub_new hub_upgrade
   @REM log the hub upgrade status to pgc log
   setlocal EnableDelayedExpansion
   FOR /F %%A IN ('WMIC OS GET LocalDateTime ^| FINDSTR \.') DO @SET B=%%A
   set logdate=!B:~0,4!-!B:~4,2!-!B:~6,2!
   set logtime=%time:~-11,2%:%time:~-8,2%:%time:~-5,2%
   set logmsg=!logdate! !logtime! [INFO] : completing hub upgrade
   echo !logmsg! >> "%MY_LOGS%"
   rename hub hub_old
   xcopy "%MY_HOME%"\hub_upgrade\* "%MY_HOME%"\ /E /Y /Q > nul
   rmdir hub_old /s /q
   rmdir hub_upgrade /s /q
   setlocal EnableDelayedExpansion
   @REM log the hub upgrade status as completed to pgc log
   FOR /F %%A IN ('WMIC OS GET LocalDateTime ^| FINDSTR \.') DO @SET B=%%A
   set logdate=!B:~0,4!-!B:~4,2!-!B:~6,2!
   set logtime=%time:~-11,2%:%time:~-8,2%:%time:~-5,2%
   set logmsg=!logdate! !logtime! [INFO] : hub upgrade completed.
   echo !logmsg! >> "%MY_LOGS%"
)

:pgc_cmd

set PYTHONPATH=%MY_HOME%\hub\scripts;%MY_HOME%\hub\scripts\lib

if NOT EXIST "%MY_HOME%\python37" goto check_python2
(
   set PATH=%MY_HOME%\python37;%PATH%
   set PYTHONHOME=%MY_HOME%\python37
   goto pgc_run
)

:check_python2

if NOT EXIST "%MY_HOME%\python2" goto pgc_run
(
   set PATH=%MY_HOME%\python2;%PATH%
   set PYTHONHOME=%MY_HOME%\python2
)

:pgc_run

python -u hub\scripts\pgc.py %*

:pgc_exit

