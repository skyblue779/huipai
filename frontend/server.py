"""
简单的前端 HTTP 服务器
"""
import http.server
import socketserver
import os
import logging
import sys
import socket

# 配置日志
logging.basicConfig(level=logging.WARNING)

PORT = 9988
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(DIRECTORY, 'dist')
SERVING_DIST = False

if os.path.isdir(DIST_DIR):
    DIRECTORY = DIST_DIR
    SERVING_DIST = True

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, directory=DIRECTORY, **kwargs)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # 忽略连接中止错误
            pass
    
    def end_headers(self):
        # 禁用缓存，便于开发
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        # 添加 CORS 支持
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()
    
    def handle_one_request(self):
        """处理单个请求，优雅处理连接中止错误"""
        try:
            super().handle_one_request()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, socket.error) as e:
            # 忽略连接中止/重置/破裂错误，这些是正常的网络事件
            pass
        except Exception as e:
            # 记录其他异常但不中断服务
            pass
    
    def handle(self):
        """处理客户端连接"""
        try:
            super().handle()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, socket.error):
            pass
    
    def log_error(self, format, *args):
        """只记录真正的错误，忽略连接中止消息"""
        if '10053' in str(args) or 'ConnectionAbortedError' in str(args):
            return
        super().log_error(format, *args)

if __name__ == '__main__':
    handler = MyHTTPRequestHandler
    # 允许端口重用
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        # Windows 默认控制台编码可能为 GBK，避免输出 emoji 触发 UnicodeEncodeError
        print(f"前端服务器运行于 http://172.16.0.66:{PORT}")
        print(f"服务目录: {DIRECTORY}")
        if not SERVING_DIST:
            print("No frontend build found. Run `npm run build` or `npm run dev`.")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            pass
        finally:
            print("\n✋ 服务器已关闭", flush=True)
