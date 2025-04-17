# Lovacia Bot main backend (FastAPI)
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Lovacia Bot is running!'}