<img src="icon_lsb-watermark-embedder.png" align="left" width="128" height="128">

# LSB Watermark Embedder

A real-time screen watermark embedding tool developed in Python. It embeds watermarks into captured screen images, supporting both visible and invisible (LSB) watermarks. Ideal for protecting screen content copyright or adding identification marks during live streaming and screen sharing.

## Features

- **Real-time Screen Capture**: High-performance screen capture, supporting primary display
- **Watermark Embedding**:
  - LSB Invisible Watermark: Using Least Significant Bit technology for imperceptible watermarking
  - Visible Watermark: Semi-transparent text watermark overlay on screen
- **Video Recording**: Save watermarked screen footage as video
- **Multilingual Support**: Traditional Chinese and English interfaces
- **Customizable Controls**:
  - Customizable watermark text
  - Selectable watermark visibility
  - Adjustable processing frequency

## Technical Implementation

- **Frontend**: HTML5, CSS3, JavaScript, WebSocket
- **Backend**: Python, FastAPI, WebSocket, OpenCV
- **Screen Capture**: MSS library
- **Watermark Algorithm**: LSB (Least Significant Bit) technique
- **Video Processing**: OpenCV, NumPy

## System Requirements

- Python 3.10+
- Windows 10+
- Minimum 4GB RAM
- Intel GPU environment support

## Installation

1. Clone this repository:
```bash
git clone https://github.com/paulchi-intel/lsb-watermark-embedder.git
cd lsb-watermark-embedder
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
# source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Launch the application:
```bash
python -m app.main
```

The application will start and be accessible at http://127.0.0.1:8000

## Usage

1. Open your browser and navigate to http://127.0.0.1:8000
2. Enter your desired watermark text in the input field
3. Choose watermark type (visible or LSB invisible)
4. Adjust processing frequency (process every N frames)
5. Click "Start" button to begin capturing screen and embedding watermarks
6. Click "Start Recording" to save the watermarked screen as video
7. Click "Stop" button when finished

## Implementation Details

### LSB Watermark Technology

LSB (Least Significant Bit) is a steganography technique that embeds information by modifying the least significant bits of pixel values in an image. These changes are almost imperceptible to the human eye. This system uses this technology to embed text watermarks into captured screen frames.

Basic steps:
1. Convert text to binary data
2. Modify the least significant bits of image pixel values to insert watermark data
3. Extract the original text from the modified image

### Visible Watermark

Visible watermarks use a semi-transparent text grid overlaid on the original image, providing intuitive copyright or content source marking. Users can customize the text content and transparency to balance visibility and image quality.

## Directory Structure

```
lsb-watermark-embedder/
├── app/                       # Main application directory
│   ├── api/                   # API implementation
│   ├── core/                  # Core modules
│   ├── models/                # Data models
│   ├── routers/               # Route handlers
│   ├── static/                # Static files
│   ├── templates/             # Frontend templates
│   ├── utils/                 # Utility functions
│   └── main.py                # Application entry
├── .vscode/                   # VS Code configuration
├── .git/                      # Git repository data
├── .gitignore                 # Git ignore configuration
├── README.md                  # Project documentation
└── requirements.txt           # Python dependencies


```

## Future Plans

- Support for multi-screen environments
- Custom watermark positioning
- Support for more watermark formats
- Enhanced watermark extraction functionality
- Support for more languages
- Custom watermark styles and effects

## About LSB Technology

LSB (Least Significant Bit) is a technique for embedding data in digital media. In digital images, each pixel consists of three RGB (Red Green Blue) color channels, each typically represented by 8 bits (values ranging from 0-255). LSB technology utilizes the least significant bits of these values for information hiding, as changing the least significant bit has minimal impact on the overall color, making it difficult for the human eye to detect.

For example, if a pixel's RGB values are (200, 150, 100), the binary representation is:
- R: 11001000
- G: 10010110
- B: 01100100

By modifying the least significant bits to (201, 151, 101), the binary representation becomes:
- R: 11001001
- G: 10010111
- B: 01100101

This change has almost no visual effect on the image but can be used to embed watermark information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact paul.chi@intel.com.

---

# 中文版 (Chinese Version)

# LSB 浮水印嵌入器

這是一個用 Python 開發的即時螢幕浮水印嵌入工具，可以將浮水印加入到螢幕擷取的影像中，支援可見和不可見(LSB)浮水印。適合用於保護螢幕內容的版權，或在直播、螢幕分享時加入識別標記。

## 功能特色

- **即時螢幕擷取**：高效能地擷取螢幕畫面，支援主螢幕
- **浮水印嵌入**：
  - LSB 不可見浮水印：使用最低有效位元（Least Significant Bit）技術嵌入浮水印
  - 可見浮水印：在螢幕上顯示半透明的文字浮水印
- **錄影功能**：將嵌入浮水印的螢幕畫面儲存為影片
- **多語言支援**：支援繁體中文和英文界面
- **自訂控制**：
  - 可自訂浮水印文字
  - 可選擇浮水印可見性
  - 可調整處理頻率

## 技術實現

- **前端技術**：HTML5, CSS3, JavaScript, WebSocket
- **後端技術**：Python, FastAPI, WebSocket, OpenCV
- **螢幕擷取**：MSS 庫
- **浮水印算法**：LSB (Least Significant Bit) 技術
- **影片處理**：OpenCV, NumPy

## 系統要求

- Python 3.10+
- Windows 10+
- 最小 4GB RAM
- 支援 Intel GPU 環境

## 安裝說明

1. 克隆此專案到本地：
```bash
git clone https://github.com/paulchi-intel/lsb-watermark-embedder.git
cd lsb-watermark-embedder
```

2. 建立並啟動虛擬環境：
```bash
python -m venv venv
# Windows 系統
venv\Scripts\activate
# Linux/Mac 系統
# source venv/bin/activate
```

3. 安裝所需依賴：
```bash
pip install -r requirements.txt
```

4. 啟動應用程式：
```bash
python -m app.main
```

應用程式將啟動，並在 http://127.0.0.1:8000 可訪問。

## 使用方法

1. 開啟瀏覽器，訪問 http://127.0.0.1:8000
2. 在浮水印文字輸入框中，輸入您想要的浮水印文字
3. 選擇浮水印類型（可見或 LSB 不可見）
4. 調整處理頻率（每 N 幀處理一次）
5. 點擊「開始」按鈕，系統將開始擷取螢幕畫面並嵌入浮水印
6. 可以點擊「開始錄影」按鈕，將嵌入浮水印的畫面保存為影片
7. 完成後點擊「停止」按鈕結束處理

## 功能實現細節

### LSB 浮水印技術

LSB（最低有效位元）是一種隱寫術技術，通過修改影像中像素的最低位元來嵌入信息，因為這些改變對人眼來說幾乎不可察覺。本系統使用這種技術將文字浮水印嵌入到螢幕擷取的畫面中。

基本步驟：
1. 將文字轉換為二進制數據
2. 修改影像像素值的最低位元，插入浮水印數據
3. 從修改後的影像中可以提取出原始文字

### 可見浮水印

可見浮水印採用半透明的文字網格覆蓋在原始影像上，提供直觀的版權或內容來源標記。用戶可以自訂文字內容和透明度，平衡可見性和影像品質。

## 目錄結構

```
lsb-watermark-embedder/
├── app/                       # 主要應用程式目錄
│   ├── api/                   # API 實現
│   ├── core/                  # 核心功能模組
│   ├── models/                # 資料模型
│   ├── routers/               # 路由處理
│   ├── static/                # 靜態檔案
│   ├── templates/             # 前端模板
│   ├── utils/                 # 工具函數
│   └── main.py                # 應用程式入口
├── .vscode/                   # VS Code configuration
├── .git/                      # Git repository data
├── .gitignore                 # Git ignore configuration
├── README.md                  # Project documentation
└── requirements.txt           # Python dependencies


```

## 未來計劃

- 支援多螢幕環境
- 自定義浮水印位置
- 支援更多浮水印格式
- 加強浮水印提取功能
- 支援更多語言
- 自定義浮水印樣式和效果

## 關於 LSB 技術

LSB（Least Significant Bit，最低有效位元）是一種在數字媒體中嵌入數據的技術。在數字圖像中，每個像素由RGB（紅綠藍）三個色彩通道組成，而每個通道通常由8位元表示（取值範圍為0-255）。LSB技術利用這些位元中的最低位進行信息藏匿，因為改變最低位對整體色彩的影響極小，人眼難以察覺。

例如，若一個像素的RGB值為(200, 150, 100)，其二進制表示為：
- R: 11001000
- G: 10010110
- B: 01100100

通過修改最低位，如改為 (201, 151, 101)，二進制表示變為：
- R: 11001001
- G: 10010111
- B: 01100101

這種變化對圖像的視覺效果幾乎沒有影響，但可以用來嵌入浮水印信息。

## 授權條款

本專案採用 MIT 授權條款 - 詳情請參閱 [LICENSE](LICENSE) 文件。

## 聯絡方式

若有任何問題或建議，請開啟一個 issue 或聯絡 paul.chi@intel.com。
