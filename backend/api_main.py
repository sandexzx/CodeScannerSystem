from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanner_handler import ScannerHandler
import os

app = FastAPI()

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Пример модели для запроса (можно расширить под твои нужды)
class ScanRequest(BaseModel):
    code: str

# Пример endpoint для сканирования кода

@app.get("/history")
def get_history():
    scanner = get_scanner()
    try:
        json_path = scanner.get_latest_json_file()
        if not json_path or not os.path.exists(json_path):
            return []
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_scanner():
    # Можно реализовать singleton или хранить в app.state
    return ScannerHandler()

@app.post("/scan")
def scan_code(req: ScanRequest):
    scanner = get_scanner()
    # Здесь логика обработки кода (пример)
    try:
        # Используем process_code для обработки кода
        result = scanner.process_code(req.code)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "Barcode Scanner API is running"}
