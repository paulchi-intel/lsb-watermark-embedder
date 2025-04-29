"""
FastAPI 主應用程式
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path
import logging
from .routers import stream

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="LSB 浮水印嵌入器")

# 靜態檔案和模板設定
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# 註冊路由
app.include_router(stream.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 