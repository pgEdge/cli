@echo off
setlocal

@REM ###################################################
@REM ######   Copyright (c) 2022-2023 pgEdge    ########
@REM ###################################################

set MY_HOME=%~sdp0
set MY_HOME=%MY_HOME:~0,-1%
set MY_LOGS=%MY_HOME%\logs\pgcli_log.out

cd /d %MY_HOME%
@REM set PATH=%SYSTEMROOT%\System32;%SYSTEMROOT%\System32\wbem;"%PATH%"

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
python -u hub\scripts\pgc.py %*

:pgc_exit

