@echo off
setlocal
pushd "%~dp0"

rem
where pyw >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" pyw -3 -m cnc_warmup
  popd
  exit /B 0
)

where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" pythonw -m cnc_warmup
  popd
  exit /B 0
)

rem
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" py -3w -m cnc_warmup
  popd
  exit /B 0
)

rem
start "" python -m cnc_warmup
popd
exit /B 0


