@echo off
rem Opens this website on http://localhost:8765 (keep this window open while you browse; close it to stop).
cd /d "%~dp0"
set PORT=8765
rem real Python only: the Microsoft Store "python" shortcut does not count
py -3 -c "import sys" >nul 2>nul && (set "RUN=py -3 -m http.server %PORT%" & goto serve)
python -c "import sys" >nul 2>nul && (set "RUN=python -m http.server %PORT%" & goto serve)
node -v >nul 2>nul && (set "RUN=npx --yes serve -l %PORT%" & goto serve)
echo Python or Node.js was not found, so the site opens straight from the folder instead.
start "" "%~dp0index.html"
pause
goto :eof
:serve
echo.
echo   Your website:  http://localhost:%PORT%/
echo   Keep this window open while you browse. Close it to stop.
echo.
rem open the browser 2 seconds later, once the server is listening
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process http://localhost:%PORT%/"
%RUN%
echo.
echo The server stopped. If it says the port is in use, another program is using %PORT%.
pause
