"""測試 Notion SA-JOP 頁面圖片抓取"""
import os, json, sys
import base64
import io
from dotenv import load_dotenv
from httpx import Client as HTTPClient

load_dotenv('C:/Projects/github/pi-mono/.env')
token = os.environ['NOTION_TOKEN']

# 建立不驗證 SSL 的 httpx client
import ssl
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

notion_client = HTTPClient(verify=False, headers={
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
})

# Page ID: SA - JOP 的 UI 與作業流程邏輯如何改頭換面
PAGE_ID = '350aad32-6752-8170-b3ec-e0d08c8f9dae'

def main():
    print(f"讀取 Notion 頁面: {PAGE_ID}")
    print("=" * 60)
    
    # 1. 讀取頁面 metadata
    try:
        resp = notion_client.get(f'https://api.notion.com/v1/pages/{PAGE_ID}')
        page = resp.json()
        title = page.get('properties', {}).get('名稱', {}).get('title', [{}])[0].get('plain_text', 'N/A')
        status = page.get('properties', {}).get('狀態', {}).get('status', {}).get('name', 'N/A')
        print(f"頁面標題: {title}")
        print(f"狀態: {status}")
        print(f"URL: {page.get('url', 'N/A')}")
    except Exception as e:
        print(f"Error reading page: {e}")
        return
    
    # 2. 讀取頁面內容（blocks）
    try:
        blocks_resp = notion_client.post(
            f'https://api.notion.com/v1/blocks/{PAGE_ID}/children',
            json={}
        )
        blocks_data = blocks_resp.json()
        block_list = blocks_data.get('results', [])
        print(f"\nPage blocks: {len(block_list)}")
        
        if not block_list:
            print("  [警告] 頁面沒有 content blocks")
            print("\n  [提示] 頁面可能沒有內容，或者內容在 database 中")
            return
        
        # 3. 找圖片
        image_blocks = []
        for i, block in enumerate(block_list):
            block_type = block.get('type', 'unknown')
            print(f"  {i+1}. {block_type}")
            
            if block_type == 'image':
                image_blocks.append(block)
                image_data = block.get('image', {})
                print(f"     Image type: {image_data.get('type', 'N/A')}")
                if image_data.get('type') == 'external':
                    print(f"     URL: {image_data.get('external', {}).get('url', 'N/A')}")
                else:
                    print(f"     File URL: {image_data.get('file', {}).get('url', 'N/A')}")
        
        print(f"\n找到 {len(image_blocks)} 張圖片")
        
        if image_blocks:
            # 4. 下載圖片並測試 Base64 編碼
            for i, img_block in enumerate(image_blocks):
                img_data = img_block.get('image', {})
                img_url = img_data.get('external', {}).get('url') or img_data.get('file', {}).get('url')
                
                if not img_url:
                    print(f"[{i+1}] 無圖片 URL，跳過")
                    continue
                
                print(f"\n[{i+1}] 下載圖片: {img_url[:80]}...")
                
                try:
                    # 下載圖片
                    resp = notion_client.get(img_url)
                    if resp.status_code == 200:
                        img_bytes = resp.content
                        
                        # 偵測 MIME type
                        content_type = resp.headers.get('content-type', 'image/jpeg')
                        mime_type = content_type.split(';')[0].strip()
                        
                        # Base64 編碼（給 Gemini 用）
                        b64 = base64.b64encode(img_bytes).decode('utf-8')
                        print(f"     Size: {len(img_bytes)} bytes")
                        print(f"     MIME: {mime_type}")
                        print(f"     Base64 length: {len(b64)}")
                        
                        # 測試開啟圖片（確認是有效圖片）
                        from PIL import Image
                        try:
                            img = Image.open(io.BytesIO(img_bytes))
                            print(f"     Image: {img.size[0]}x{img.size[1]} {img.format}")
                        except ImportError:
                            print(f"     [提示] PIL 未安裝，跳過圖片驗證")
                        except Exception as e:
                            print(f"     [警告] 無法開啟圖片: {e}")
                    else:
                        print(f"     [錯誤] HTTP {resp.status_code}")
                        
                except Exception as e:
                    print(f"     [錯誤] {e}")
    
    except Exception as e:
        print(f"Error listing blocks: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == '__main__':
    main()
