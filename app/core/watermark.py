import cv2
import numpy as np
import mss
import pygetwindow as gw
from typing import Optional, Tuple, Dict
import socket

class WatermarkProcessor:
    def __init__(self):
        """初始化浮水印處理器"""
        self.device_name = socket.gethostname()
        self.watermark = self.device_name
        self.sct = mss.mss()
        self.is_processing = False
        self.frame_counter = 0
        self.process_interval = 5  # 預設每5幀處理一次

    def capture_screen(self) -> np.ndarray:
        """擷取螢幕畫面
        
        Returns:
            np.ndarray: 擷取的畫面
        """
        monitor = self.sct.monitors[1]  # 主螢幕
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def add_lsb_watermark(self, frame: np.ndarray, watermark_text: str) -> np.ndarray:
        """使用LSB技術將浮水印嵌入影格
        
        Args:
            frame (np.ndarray): 原始影格
            watermark_text (str): 浮水印文字
            
        Returns:
            np.ndarray: 嵌入浮水印後的影格
        """
        # 將浮水印文字轉換為二進制
        watermark_bin = ''.join([format(ord(char), '08b') for char in watermark_text])
        
        # 複製影格以避免修改原始資料
        result = frame.copy()
        
        # 檢查影格大小是否足夠
        if result.shape[0] * result.shape[1] < len(watermark_bin):
            return frame
        
        # 嵌入浮水印
        watermark_idx = 0
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                for k in range(3):  # RGB channels
                    if watermark_idx < len(watermark_bin):
                        # 修改最低位
                        result[i, j, k] = (result[i, j, k] & 0xFE) | int(watermark_bin[watermark_idx])
                        watermark_idx += 1
                    else:
                        return result
        return result

    def add_visible_watermark(self, frame: np.ndarray, watermark_text: str) -> np.ndarray:
        """在影格上添加可見浮水印
        
        Args:
            frame (np.ndarray): 原始影格
            watermark_text (str): 浮水印文字
            
        Returns:
            np.ndarray: 添加浮水印後的影格
        """
        result = frame.copy()
        
        # 設定文字屬性
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        font_thickness = 2
        
        # 獲取文字大小
        (text_width, text_height), _ = cv2.getTextSize(watermark_text, font, font_scale, font_thickness)
        
        # 計算文字位置（正中央）
        x = (result.shape[1] - text_width) // 2
        y = (result.shape[0] + text_height) // 2
        
        # 繪製白色背景
        cv2.rectangle(result, 
                     (x - 10, y - text_height - 10),
                     (x + text_width + 10, y + 10),
                     (255, 255, 255),
                     -1)
        
        # 繪製文字
        cv2.putText(result, watermark_text, (x, y), font, font_scale, (0, 0, 0), font_thickness)
        
        return result

    def process_frame(self, frame: np.ndarray, watermark_text: str, 
                     is_visible: bool = False) -> Tuple[np.ndarray, bool]:
        """處理影格，根據設定添加浮水印
        
        Args:
            frame (np.ndarray): 原始影格
            watermark_text (str): 浮水印文字
            is_visible (bool): 是否使用可見浮水印
            
        Returns:
            Tuple[np.ndarray, bool]: (處理後的影格, 是否有處理)
        """
        self.frame_counter += 1
        
        # 檢查是否需要處理這一幀
        if self.frame_counter % self.process_interval != 0:
            return frame, False
            
        # 根據可見性選擇處理方法
        if is_visible:
            return self.add_visible_watermark(frame, watermark_text), True
        else:
            return self.add_lsb_watermark(frame, watermark_text), True

    def extract_watermark(self, frame: np.ndarray, length: int) -> str:
        """從影格中提取浮水印
        
        Args:
            frame (np.ndarray): 包含浮水印的影格
            length (int): 浮水印文字長度
            
        Returns:
            str: 提取出的浮水印文字
        """
        binary_data = ""
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                for k in range(3):
                    binary_data += str(frame[i, j, k] & 1)
                    if len(binary_data) >= length * 8:
                        break
                if len(binary_data) >= length * 8:
                    break
            if len(binary_data) >= length * 8:
                break
                
        # 將二進制轉換回文字
        extracted_text = ""
        for i in range(0, length * 8, 8):
            byte = binary_data[i:i+8]
            extracted_text += chr(int(byte, 2))
            
        return extracted_text

    def set_process_interval(self, interval: int) -> None:
        """設定處理間隔
        
        Args:
            interval (int): 處理間隔（每N幀處理一次）
        """
        self.process_interval = max(1, min(30, interval))  # 限制在1-30之間

    def cleanup(self) -> None:
        """清理資源"""
        self.sct.close() 