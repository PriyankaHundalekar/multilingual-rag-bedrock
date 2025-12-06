@echo off
echo Cleaning Python cache...
del /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul
echo.
echo Starting AI for Bharat RAG System...
echo.
streamlit run app.py --server.port 8501
