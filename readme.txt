run commands:
    make virtual env: python -m venv ankit
    activate venv: ankit\scripts\activate  
    install requirements: pip install requirements.txt

    then
        cd app
    
    then first run backend
        uvicorn main:app --reload
    
    then  run frontend
        streamlit run app.py