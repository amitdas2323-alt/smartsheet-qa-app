@echo off
cd /d "%~dp0"
echo Starting Smartsheet web app...
echo.
echo When you see "You can now view your Streamlit app in your browser" below,
echo open a browser and go to:  http://localhost:8501
echo.
echo Keep this window OPEN while using the app. Press Ctrl+C to stop.
echo.

REM Use python -m so streamlit is found even when not on PATH
python -m streamlit run app_streamlit.py --server.address 0.0.0.0
if errorlevel 1 (
    echo.
    echo App exited with an error. If you see "No module named streamlit", run:
    echo   pip install -r requirements.txt
    echo Then run this batch file again.
)
pause
