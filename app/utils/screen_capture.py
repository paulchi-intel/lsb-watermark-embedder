"""
螢幕擷取工具模組
"""
import cv2
import numpy as np
import mss
from typing import Tuple, Optional, List
from datetime import datetime
import os
import glob

class ScreenCapture:
    """螢幕擷取工具類別"""
    
    def __init__(self):
        """初始化螢幕擷取工具"""
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # 預設使用主螢幕
        self.watermark_text = ""
        self.watermark_visible = False
        self.is_processing = False
        self.frame_interval = 5
        self.frame_count = 0
        self.use_redundancy = False  # 是否使用冗餘浮水印
        
        # 錄影相關
        self.is_recording = False
        self.video_writer = None
        self.fps = 30.0
        self.output_dir = "recorded_video"
        self.screenshot_dir = "screen_shot"
        self.current_recording_path = None
    
    def set_watermark(self, text: str, visible: bool = False, redundancy: bool = False):
        """
        設定浮水印
        
        Args:
            text: 浮水印文字
            visible: 是否為可見浮水印
            redundancy: 是否使用冗餘浮水印（僅對不可見浮水印有效）
        """
        self.watermark_text = text
        self.watermark_visible = visible
        self.use_redundancy = redundancy
    
    def set_processing(self, enabled: bool):
        """
        設定是否進行處理
        
        Args:
            enabled: 是否啟用處理
        """
        self.is_processing = enabled
        self.frame_count = 0
    
    def set_frame_interval(self, interval: int):
        """
        設定處理頻率
        
        Args:
            interval: 每 N 幀處理一次
        """
        self.frame_interval = max(1, min(30, interval))
    
    def add_visible_watermark(self, frame: np.ndarray) -> np.ndarray:
        """
        添加可見浮水印，只在畫面正中央顯示一個浮水印
        
        Args:
            frame: 輸入影像
        
        Returns:
            添加浮水印後的影像
        """
        if not self.watermark_text:
            return frame
            
        height, width = frame.shape[:2]
        # 創建浮水印層
        overlay = frame.copy()
        
        # 設定文字參數
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(width, height) / 500.0  # 增大字體大小
        thickness = max(2, int(font_scale * 3))  # 增加文字粗細
        color = (255, 255, 255)  # 白色文字
        
        # 取得文字大小
        text_size = cv2.getTextSize(self.watermark_text, font, font_scale, thickness)[0]
        
        # 計算中心位置
        x = (width - text_size[0]) // 2
        y = (height + text_size[1]) // 2
        
        # 繪製文字陰影（加粗陰影）
        cv2.putText(overlay, self.watermark_text, 
                  (x+3, y+3), font, font_scale, 
                  (0,0,0), thickness+1)  # 增加陰影粗細
        # 繪製文字
        cv2.putText(overlay, self.watermark_text, 
                  (x, y), font, font_scale, 
                  color, thickness)
        
        # 設定透明度
        alpha = 0.35  # 稍微提高透明度
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    
    def add_visible_watermark_redundancy(self, frame: np.ndarray) -> np.ndarray:
        """
        添加可見浮水印，重複填滿整個畫面
        
        Args:
            frame: 輸入影像
        
        Returns:
            添加浮水印後的影像
        """
        if not self.watermark_text:
            return frame
            
        height, width = frame.shape[:2]
        # 創建浮水印層
        overlay = frame.copy()
        
        # 設定文字參數
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(width, height) / 1000.0  # 增大字體大小
        thickness = max(2, int(font_scale * 3))  # 增加文字粗細
        color = (255, 255, 255)  # 白色文字
        
        # 取得文字大小
        text_size = cv2.getTextSize(self.watermark_text, font, font_scale, thickness)[0]
        
        # 計算間距
        spacing_x = text_size[0] + 80  # 增加水平間距
        spacing_y = text_size[1] + 80  # 增加垂直間距
        
        # 計算需要的行數和列數
        rows = height // spacing_y + 2
        cols = width // spacing_x + 2
        
        # 計算起始位置（使文字網格居中）
        start_x = (width % spacing_x) // 2 - spacing_x
        start_y = (height % spacing_y) // 2
        
        # 繪製文字網格
        for row in range(rows):
            y = start_y + row * spacing_y
            # 偏移每一行，創造交錯效果
            offset_x = (row % 2) * (spacing_x // 2)
            
            for col in range(cols):
                x = start_x + col * spacing_x + offset_x
                
                # 繪製文字陰影（加粗陰影）
                cv2.putText(overlay, self.watermark_text, 
                          (x+3, y+3), font, font_scale, 
                          (0,0,0), thickness+1)  # 增加陰影粗細
                # 繪製文字
                cv2.putText(overlay, self.watermark_text, 
                          (x, y), font, font_scale, 
                          color, thickness)
        
        # 設定透明度
        alpha = 0.35  # 稍微提高透明度
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    
    def add_invisible_watermark(self, frame: np.ndarray) -> np.ndarray:
        """
        添加不可見浮水印（LSB）
        
        Args:
            frame: 輸入影像
        
        Returns:
            添加浮水印後的影像
        """
        if not self.watermark_text:
            return frame
            
        # 將文字轉換為二進制
        binary_text = ''.join(format(ord(c), '08b') for c in self.watermark_text)
        binary_text += '0' * 8  # 添加結束標記
        
        # 確保有足夠的像素來嵌入浮水印
        height, width = frame.shape[:2]
        if len(binary_text) > (height * width):
            return frame
        
        # 複製影像
        watermarked = frame.copy()
        
        # 嵌入浮水印
        idx = 0
        for i in range(height):
            for j in range(width):
                if idx < len(binary_text):
                    # 修改藍色通道的最低位
                    pixel = watermarked[i, j].copy()
                    pixel[0] = (pixel[0] & 0xFE) | int(binary_text[idx])
                    watermarked[i, j] = pixel
                    idx += 1
                else:
                    break
        
        return watermarked
    
    def add_invisible_watermark_redundancy(self, frame: np.ndarray) -> np.ndarray:
        """
        添加帶有冗餘的不可見浮水印（LSB），提高浮水印的魯棒性
        
        Args:
            frame: 輸入影像
        
        Returns:
            添加浮水印後的影像
        """
        if not self.watermark_text:
            return frame
            
        # 準備要嵌入的文字，添加特殊的結束標記
        watermark = self.watermark_text + '\0'  # 添加空字符作為結束標記
        watermark_bin = ''.join([format(ord(char), '08b') for char in watermark])
        
        # 確保圖片夠大來存放浮水印
        height, width = frame.shape[:2]
        if height * width * 3 < len(watermark_bin) * 10:  # 預留足夠空間
            print("圖片太小，無法嵌入完整的浮水印")
            return frame
        
        # 複製影像
        watermarked = frame.copy()
        
        # 固定種子以確保提取時能復現相同的隨機序列
        seed_value = 42
        import random
        random.seed(seed_value)
        
        # 創建圖像大小的偽隨機排列用於嵌入
        positions = []
        
        # 建立像素位置列表 (行, 列, 通道)
        for i in range(height):
            for j in range(width):
                for k in range(3):  # RGB通道
                    positions.append((i, j, k))
        
        # 隨機化位置順序
        random.shuffle(positions)
        
        # 確保每一位浮水印信息至少有10個不同位置
        redundancy = 10
        
        # 嵌入浮水印（每個位元重複嵌入多次以提高魯棒性）
        for watermark_idx in range(len(watermark_bin)):
            bit = int(watermark_bin[watermark_idx])
            # 將相同的位元嵌入多個不同位置以提高魯棒性
            for r in range(redundancy):
                if watermark_idx * redundancy + r < len(positions):
                    i, j, k = positions[watermark_idx * redundancy + r]
                    watermarked[i, j, k] = (watermarked[i, j, k] & 0xFE) | bit
        
        # 在文件開頭存儲種子值和冗餘度（用於提取時恢復）
        # 存儲種子值（32位整數）
        seed_bin = format(seed_value, '032b')
        for idx, bit in enumerate(seed_bin):
            i, j, k = idx // 3, (idx % 3) // 3, idx % 3
            watermarked[i, j, k] = (watermarked[i, j, k] & 0xFE) | int(bit)
            
        # 存儲冗餘度（8位整數）
        redundancy_bin = format(redundancy, '08b')
        for idx, bit in enumerate(redundancy_bin):
            i, j, k = (idx + 32) // 3, ((idx + 32) % 3) // 3, (idx + 32) % 3
            watermarked[i, j, k] = (watermarked[i, j, k] & 0xFE) | int(bit)
            
        print(f"浮水印數據已分散嵌入到整個圖像中，每個位元重複嵌入{redundancy}次")
        return watermarked
    
    def start_recording(self) -> Optional[str]:
        """
        開始錄影
        
        Returns:
            Optional[str]: 錄影檔案路徑，如果失敗則返回 None
        """
        try:
            if self.is_recording:
                return None
                
            # 確保輸出目錄存在
            os.makedirs(self.output_dir, exist_ok=True)
            
            # 生成輸出檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"recording_{timestamp}.mp4")
            
            # 取得一幀來決定影片大小
            frame = self.capture_screen()
            if frame is None:
                return None
            
            height, width = frame.shape[:2]
            
            # 創建視頻寫入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                output_path, fourcc, self.fps, (width, height)
            )
            
            self.is_recording = True
            self.current_recording_path = output_path  # 保存當前錄影路徑
            print(f"開始錄影: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"開始錄影失敗: {str(e)}")
            return None
    
    def stop_recording(self) -> Optional[str]:
        """
        停止錄影
        
        Returns:
            Optional[str]: 錄影檔案路徑，如果失敗則返回 None
        """
        try:
            if not self.is_recording:
                return None
            
            self.is_recording = False
            recording_path = self.current_recording_path
            
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            print("停止錄影")
            return recording_path
            
        except Exception as e:
            print(f"停止錄影失敗: {str(e)}")
            return None
    
    def capture_screen(self) -> Optional[np.ndarray]:
        """
        擷取螢幕畫面
        
        Returns:
            np.ndarray: 擷取的畫面，如果失敗則返回 None
        """
        try:
            # 擷取螢幕畫面
            screenshot = self.sct.grab(self.monitor)
            
            # 轉換為 numpy 陣列
            frame = np.array(screenshot)
            
            # 轉換色彩空間從 BGRA 到 BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # 如果正在處理且到達處理間隔
            if self.is_processing and self.frame_count % self.frame_interval == 0:
                if self.watermark_visible:
                    if self.use_redundancy:
                        frame = self.add_visible_watermark_redundancy(frame)
                    else:
                        frame = self.add_visible_watermark(frame)
                else:
                    if self.use_redundancy:
                        frame = self.add_invisible_watermark_redundancy(frame)
                    else:
                        frame = self.add_invisible_watermark(frame)
            
            # 更新幀計數
            self.frame_count = (self.frame_count + 1) % self.frame_interval
            
            # 如果正在錄影，寫入影格
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)
            
            return frame
        except Exception as e:
            print(f"螢幕擷取失敗: {str(e)}")
            return None
    
    def get_frame_jpeg(self) -> Tuple[bool, bytes]:
        """
        取得 JPEG 格式的畫面
        
        Returns:
            Tuple[bool, bytes]: (是否成功, JPEG 資料)
        """
        frame = self.capture_screen()
        if frame is None:
            return False, b''
        
        # 將畫面編碼為 JPEG
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            return False, b''
        
        return True, jpeg.tobytes()
    
    def take_screenshot(self, base64_data: str = None) -> str:
        """
        擷取目前畫面並儲存為圖檔
        
        Args:
            base64_data: 可選的Base64圖像數據，若提供則使用此數據而非擷取新畫面
            
        Returns:
            str: 圖檔儲存路徑，失敗則返回空字串
        """
        try:
            # 確保目錄存在
            os.makedirs(self.screenshot_dir, exist_ok=True)
            
            # 生成檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.bmp")
            
            print(f"準備擷取螢幕截圖並儲存至: {file_path}")
            
            # 如果提供了Base64數據，直接使用
            if base64_data:
                # 移除 data:image/png;base64, 前綴
                if ',' in base64_data:
                    base64_data = base64_data.split(',')[1]
                
                try:
                    # 解碼Base64並寫入檔案
                    import base64
                    img_data = base64.b64decode(base64_data)
                    print(f"成功解碼 Base64 數據，長度: {len(img_data)}")
                    
                    # 擷取畫面
                    frame = self.capture_screen()
                    if frame is None:
                        print("無法擷取畫面")
                        return ""
                    
                    # 儲存原始畫面
                    print(f"儲存螢幕截圖至: {file_path}")
                    cv2.imwrite(file_path, frame)
                    
                except Exception as e:
                    print(f"處理 Base64 數據時發生錯誤: {str(e)}")
                    return ""
            else:
                # 擷取畫面
                frame = self.capture_screen()
                if frame is None:
                    print("無法擷取畫面")
                    return ""
                
                # 儲存截圖
                print(f"儲存螢幕截圖至: {file_path}")
                cv2.imwrite(file_path, frame)
            
            print(f"螢幕截圖已儲存: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"擷取螢幕截圖失敗: {str(e)}")
            return ""
    
    def get_latest_screenshots(self, count: int = 2, pattern: str = "screenshot_*.bmp") -> List[str]:
        """
        獲取最近的 N 張截圖
        
        Args:
            count: 要獲取的截圖數量
            pattern: 檔案名稱模式
            
        Returns:
            List[str]: 截圖文件路徑列表
        """
        try:
            # 確保目錄存在
            if not os.path.exists(self.screenshot_dir):
                return []
                
            # 獲取指定模式的檔案
            files = glob.glob(os.path.join(self.screenshot_dir, pattern))
            
            # 根據修改時間排序
            files.sort(key=os.path.getmtime, reverse=True)
            
            # 返回最近的 N 張
            return files[:count]
        except Exception as e:
            print(f"獲取截圖列表失敗: {str(e)}")
            return []
    
    def compare_screenshots(self) -> Optional[str]:
        """
        比較最近的兩張截圖並生成差異圖
        
        Returns:
            Optional[str]: 差異圖片的路徑，失敗則返回 None
        """
        try:
            # 獲取最近的兩張原始截圖
            screenshots = self.get_latest_screenshots(2, "screenshot_*.bmp")
            
            # 檢查是否有足夠的截圖
            if len(screenshots) < 2:
                print(f"沒有足夠的截圖可比較，僅找到 {len(screenshots)} 張")
                return None
            
            # 讀取兩張圖片
            img1 = cv2.imread(screenshots[0])
            img2 = cv2.imread(screenshots[1])
            
            if img1 is None or img2 is None:
                print("無法讀取圖片檔案")
                return None
                
            # 確保兩張圖片大小相同
            if img1.shape != img2.shape:
                print("兩張圖片大小不同，調整大小")
                # 調整第二張圖片大小以匹配第一張
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 計算差異
            difference = cv2.absdiff(img1, img2)
            
            # 為了讓差異更容易看到，將差異值放大
            # 先轉換為浮點數類型，再進行放大
            difference_amplified = difference.astype(np.float32) * 1000
            # 將超過255的值限制在255
            difference_amplified = np.clip(difference_amplified, 0, 255).astype(np.uint8)
            
            # 生成差異圖片的檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            difference_path = os.path.join(self.screenshot_dir, f"difference_{timestamp}.bmp")
            
            # 儲存差異圖片
            cv2.imwrite(difference_path, difference_amplified)
            
            # 創建一個合併的對比圖（原圖1、原圖2、差異圖）
            # 先創建一個空白圖像，高度相同，寬度是三個圖的總和
            h, w = img1.shape[:2]
            comparison = np.zeros((h, w * 3, 3), dtype=np.uint8)
            
            # 將三張圖片放入合併圖
            comparison[:, :w] = img1
            comparison[:, w:w*2] = img2
            comparison[:, w*2:] = difference_amplified
            
            # 添加標籤
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            font_color = (255, 255, 255)
            
            # 標註圖片
            cv2.putText(comparison, f"Screenshot 1: {os.path.basename(screenshots[0])}", 
                      (10, 30), font, font_scale, font_color, font_thickness)
            cv2.putText(comparison, f"Screenshot 2: {os.path.basename(screenshots[1])}", 
                      (w + 10, 30), font, font_scale, font_color, font_thickness)
            cv2.putText(comparison, "Difference (x1000)", 
                      (w*2 + 10, 30), font, font_scale, font_color, font_thickness)
            
            # 保存對比圖
            comparison_path = os.path.join(self.screenshot_dir, f"comparison_{timestamp}.bmp")
            cv2.imwrite(comparison_path, comparison)
            
            print(f"截圖比較完成，差異圖片已儲存: {comparison_path}")
            return comparison_path
            
        except Exception as e:
            print(f"比較截圖失敗: {str(e)}")
            return None
    
    def screenshot_and_compare(self) -> Optional[str]:
        """
        擷取螢幕畫面，同時產生無浮水印和有浮水印版本，並比較兩者差異
        
        Returns:
            Optional[str]: 比較圖片的路徑，失敗則返回 None
        """
        try:
            # 確保目錄存在
            os.makedirs(self.screenshot_dir, exist_ok=True)
            
            # 生成截圖檔案名稱（使用時間戳以確保唯一性）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.bmp")
            watermarked_path = os.path.join(self.screenshot_dir, f"watermarked_{timestamp}.bmp")
            difference_path = os.path.join(self.screenshot_dir, f"difference_{timestamp}.bmp")
            comparison_path = os.path.join(self.screenshot_dir, f"comparison_{timestamp}.bmp")
            
            # 擷取畫面
            print("擷取螢幕畫面...")
            frame = self.capture_screen()
            if frame is None:
                print("無法擷取畫面")
                return None
            
            # 儲存原始畫面（無浮水印）
            print(f"儲存原始截圖至: {screenshot_path}")
            cv2.imwrite(screenshot_path, frame)
            
            # 檢查浮水印文字是否為空
            if not self.watermark_text:
                print("警告：沒有設定浮水印文字，將使用預設文字")
                temp_watermark = self.watermark_text
                self.watermark_text = "LSB Watermark"
            
            print(f"準備嵌入浮水印，文字: {self.watermark_text}")
            
            # 嵌入浮水印（根據可視性與冗餘選項）
            if self.watermark_visible:
                print("使用可見浮水印模式")
                watermarked_frame = self.add_visible_watermark(frame)
            elif self.use_redundancy:
                print("使用冗餘浮水印模式（LSB冗餘）")
                watermarked_frame = self.add_invisible_watermark_redundancy(frame)
            else:
                print("使用標準浮水印模式（LSB）")
                watermarked_frame = self.add_invisible_watermark(frame)
            
            # 檢查是否確實修改了圖像
            diff = cv2.absdiff(frame, watermarked_frame)
            diff_sum = np.sum(diff)
            print(f"圖像差異總和: {diff_sum}")
            
            if diff_sum == 0:
                print("警告：浮水印嵌入後與原始圖像沒有差異，將添加標記")
                h, w = watermarked_frame.shape[:2]
                mark_size = min(10, h // 100, w // 100)
                mark_x = w - mark_size - 5
                mark_y = h - mark_size - 5
                watermarked_frame[mark_y:mark_y+mark_size, mark_x:mark_x+mark_size, 0] = (
                    watermarked_frame[mark_y:mark_y+mark_size, mark_x:mark_x+mark_size, 0] & 0xFE
                )
            
            if 'temp_watermark' in locals():
                self.watermark_text = temp_watermark
            
            # 儲存浮水印畫面
            print(f"儲存浮水印截圖至: {watermarked_path}")
            cv2.imwrite(watermarked_path, watermarked_frame)
            
            # 產生差異圖
            print("產生差異圖...")
            difference_amplified = diff.astype(np.float32) * 1000
            difference_amplified = np.clip(difference_amplified, 0, 255).astype(np.uint8)
            cv2.imwrite(difference_path, difference_amplified)
            print(f"差異圖片已儲存至: {difference_path}")
            
            # 合併對比圖
            h, w = frame.shape[:2]
            comparison = np.zeros((h, w * 3, 3), dtype=np.uint8)
            comparison[:, :w] = frame
            comparison[:, w:w*2] = watermarked_frame
            comparison[:, w*2:] = difference_amplified
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            font_color = (255, 255, 255)
            cv2.putText(comparison, "Original", (10, 30), font, font_scale, font_color, font_thickness)
            cv2.putText(comparison, "Watermarked", (w + 10, 30), font, font_scale, font_color, font_thickness)
            cv2.putText(comparison, "Difference (x1000)", (w*2 + 10, 30), font, font_scale, font_color, font_thickness)
            cv2.imwrite(comparison_path, comparison)
            print(f"對比圖已儲存至: {comparison_path}")
            return comparison_path
        except Exception as e:
            print(f"截圖及比較失敗: {str(e)}")
            return None
    
    def get_comparison_jpeg(self) -> Tuple[bool, bytes, str]:
        """
        比較最近的兩張截圖並生成差異圖，返回JPEG格式數據
        
        Returns:
            Tuple[bool, bytes, str]: (是否成功, JPEG圖像數據, 比較圖像路徑)
        """
        try:
            # 先調用現有的比較方法生成圖像文件
            comparison_path = self.compare_screenshots()
            
            if comparison_path is None:
                return False, b'', ""
            
            # 讀取比較圖像
            comparison_img = cv2.imread(comparison_path)
            if comparison_img is None:
                return False, b'', ""
            
            # 轉換為JPEG格式
            ret, jpeg = cv2.imencode('.jpg', comparison_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            if not ret:
                return False, b'', ""
            
            return True, jpeg.tobytes(), comparison_path
            
        except Exception as e:
            print(f"獲取比較圖像失敗: {str(e)}")
            return False, b'', ""
    
    def __del__(self):
        """清理資源"""
        self.stop_recording()  # 確保錄影停止
        self.sct.close() 