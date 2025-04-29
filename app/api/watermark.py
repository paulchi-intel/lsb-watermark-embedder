from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import json
import cv2
import numpy as np
import base64
from ..core.watermark import WatermarkProcessor
import asyncio
import time
import psutil
import logging

router = APIRouter()
processor = WatermarkProcessor()

# 用於追蹤活動的 WebSocket 連接
active_connections: Dict[str, WebSocket] = {}

class WatermarkState:
    def __init__(self):
        self.is_processing = False
        self.watermark_text = ""
        self.is_visible = False
        self.process_interval = 5
        self.start_time = 0
        self.frame_count = 0

    def start_processing(self):
        self.is_processing = True
        self.start_time = time.time()
        self.frame_count = 0

    def stop_processing(self):
        self.is_processing = False

    def update_frame_count(self):
        self.frame_count += 1

    def get_fps(self) -> float:
        if not self.is_processing:
            return 0
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:
            return 0
        return self.frame_count / elapsed_time

state = WatermarkState()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(id(websocket))
    active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            command = json.loads(data)
            
            if command["type"] == "start":
                state.watermark_text = command.get("watermark_text", "")
                state.is_visible = command.get("is_visible", False)
                state.process_interval = command.get("process_interval", 5)
                processor.set_process_interval(state.process_interval)
                state.start_processing()
                
            elif command["type"] == "stop":
                state.stop_processing()
                
            elif command["type"] == "update_settings":
                if "watermark_text" in command:
                    state.watermark_text = command["watermark_text"]
                if "is_visible" in command:
                    state.is_visible = command["is_visible"]
                if "process_interval" in command:
                    state.process_interval = command["process_interval"]
                    processor.set_process_interval(state.process_interval)
                    
            # 發送性能數據
            if state.is_processing:
                performance_data = {
                    "type": "performance",
                    "fps": round(state.get_fps(), 1),
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": round(psutil.Process().memory_info().rss / 1024 / 1024, 1),  # MB
                    "latency": round(time.time() * 1000) % 100  # 模擬延遲數據
                }
                await websocket.send_json(performance_data)
                
    except WebSocketDisconnect:
        state.stop_processing()
        del active_connections[client_id]
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        state.stop_processing()
        if client_id in active_connections:
            del active_connections[client_id]

@router.websocket("/stream")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            if not state.is_processing:
                await asyncio.sleep(0.1)
                continue
                
            # 擷取並處理影格
            frame = processor.capture_screen()
            processed_frame, was_processed = processor.process_frame(
                frame, 
                state.watermark_text,
                state.is_visible
            )
            
            # 更新幀計數
            state.update_frame_count()
            
            # 轉換為 JPEG 格式
            _, buffer = cv2.imencode('.jpg', processed_frame)
            
            # 轉換為 base64 字串
            frame_data = base64.b64encode(buffer).decode('utf-8')
            
            # 發送影格
            await websocket.send_json({
                "type": "frame",
                "data": frame_data,
                "processed": was_processed
            })
            
            # 控制更新頻率
            await asyncio.sleep(1/30)  # 限制最大 FPS 為 30
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logging.error(f"Video stream error: {str(e)}") 