@echo off
setlocal
pushd "%~dp0"

if "%~1"=="" (
  echo Usage: %~nx0 --x-travel N --y-travel N --z-travel N [options]
  echo   Options: --controller tnc640^|fanuc31i --program-name NAME --start-rpm N --finish-rpm N --start-feed N --finish-feed N --rpm-steps N --seconds-per-step N --coolant --output PATH
  echo   Example: %~nx0 --controller tnc640 --program-name WARMUP --x-travel 762 --y-travel 508 --z-travel 500 --start-rpm 500 --finish-rpm 6000 --start-feed 1000 --finish-feed 2000 --rpm-steps 5 --seconds-per-step 60 --coolant --output warmup.h
  popd
  exit /B 1
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -m cnc_warmup %*
) else (
  python -m cnc_warmup %*
)

set ERR=%ERRORLEVEL%
popd
exit /B %ERR%


