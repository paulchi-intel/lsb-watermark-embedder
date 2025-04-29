"""
串流路由處理模組
"""
from fastapi import APIRouter, WebSocket
from ..utils.screen_capture import ScreenCapture
import asyncio
import json
from typing import Dict, Any
import os
import subprocess
import platform

router = APIRouter()
screen_capture = ScreenCapture()

async def open_folder(path):
    """開啟檔案總管並顯示指定路徑"""
    try:
        if platform.system() == "Windows":
            os.startfile(os.path.dirname(path))
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", os.path.dirname(path)])
        else:  # Linux
            subprocess.run(["xdg-open", os.path.dirname(path)])
        return True
    except Exception as e:
        print(f"無法開啟檔案總管: {e}")
        return False

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端點，用於串流螢幕畫面
    """
    await websocket.accept()
    
    # 建立訊息處理任務
    async def handle_messages():
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get('type') == 'config':
                    config = message.get('data', {})
                    if 'watermarkText' in config:
                        screen_capture.set_watermark(
                            config['watermarkText'],
                            config.get('watermarkVisible', False),
                            config.get('watermarkRedundancy', False)
                        )
                    if 'frameInterval' in config:
                        screen_capture.set_frame_interval(int(config['frameInterval']))
                    if 'processing' in config:
                        screen_capture.set_processing(config['processing'])
                
                elif message.get('type') == 'screenshot':
                    try:
                        # 處理截圖請求 - 只進行螢幕截圖，不嵌入浮水印
                        screenshot_path = screen_capture.take_screenshot(message.get('data'))
                        if screenshot_path:
                            await websocket.send_json({
                                "type": "screenshot",
                                "status": "success",
                                "screenshot_path": str(screenshot_path)
                            })
                            # 自動打開包含截圖的文件夾
                            await open_folder(screenshot_path)
                        else:
                            await websocket.send_json({
                                "type": "screenshot",
                                "status": "error",
                                "message": "截圖失敗"
                            })
                    except Exception as e:
                        print(f"截圖錯誤: {str(e)}")
                        await websocket.send_json({
                            "type": "screenshot",
                            "status": "error",
                            "message": f"截圖錯誤: {str(e)}"
                        })
                elif message.get('type') == 'compare_images':
                    try:
                        # 執行截圖、加浮水印、比較的整合流程
                        comparison_path = screen_capture.screenshot_and_compare()
                        if comparison_path:
                            # 先發送成功消息
                            await websocket.send_json({
                                "type": "compare_images",
                                "status": "success",
                                "message": "截圖比較完成",
                                "comparison_path": str(comparison_path)
                            })
                            
                            # 獲取並發送比較圖像
                            try:
                                with open(comparison_path, 'rb') as f:
                                    image_data = f.read()
                                await websocket.send_bytes(image_data)
                            except Exception as img_error:
                                print(f"發送比較圖像失敗: {str(img_error)}")
                            
                            # 自動打開包含比較圖片的文件夾
                            await open_folder(comparison_path)
                        else:
                            await websocket.send_json({
                                "type": "compare_images",
                                "status": "error",
                                "message": "截圖比較失敗"
                            })
                    except Exception as e:
                        print(f"比較截圖錯誤: {str(e)}")
                        await websocket.send_json({
                            "type": "compare_images",
                            "status": "error",
                            "message": f"比較截圖錯誤: {str(e)}"
                        })
                elif message.get('type') == 'open_folder':
                    success = await open_folder(message.get('path'))
                    if not success:
                        await websocket.send_json({
                            "type": "error",
                            "message": "無法開啟檔案總管"
                        })
                
            except Exception as e:
                print(f"接收訊息錯誤: {str(e)}")
                break
    
    # 建立畫面串流任務
    async def stream_frames():
        while True:
            try:
                success, frame_data = screen_capture.get_frame_jpeg()
                if success:
                    await websocket.send_bytes(frame_data)
                await asyncio.sleep(1/30)  # 30 FPS
            except Exception as e:
                print(f"串流畫面錯誤: {str(e)}")
                break
    
    try:
        # 同時執行訊息處理和畫面串流
        await asyncio.gather(
            handle_messages(),
            stream_frames()
        )
    except Exception as e:
        print(f"WebSocket 錯誤: {str(e)}")
    finally:
        await websocket.close()