@echo off
rem Opens this website on http://localhost:8080 (keep this window open while you browse).
cd /d "%~dp0"
where python >nul 2>nul && (start "" http://localhost:8080/ & python -m http.server 8080 & goto :eof)
where py >nul 2>nul && (start "" http://localhost:8080/ & py -m http.server 8080 & goto :eof)
where npx >nul 2>nul && (start "" http://localhost:8080/ & npx --yes serve -l 8080 & goto :eof)
echo Python or Node.js was not found, so opening the site straight from the folder instead.
start "" "%~dp0index.html"
pause
