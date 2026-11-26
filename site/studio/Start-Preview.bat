@echo off
rem Opens this website on http://localhost:8765 (keep this window open while you browse).
cd /d "%~dp0"
where python >nul 2>nul && (start "" http://localhost:8765/ & python -m http.server 8765 & goto :eof)
where py >nul 2>nul && (start "" http://localhost:8765/ & py -m http.server 8765 & goto :eof)
where npx >nul 2>nul && (start "" http://localhost:8765/ & npx --yes serve -l 8765 & goto :eof)
echo Python or Node.js was not found, so opening the site straight from the folder instead.
start "" "%~dp0index.html"
pause
