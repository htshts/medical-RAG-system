"""
最小测试服务器
验证 Python http.server 是否可以正常运行
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"status": "ok", "message": "Test server is running"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # 禁用默认日志

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8888), TestHandler)
    print("Test server starting on http://localhost:8888")
    print("Press Ctrl+C to stop")
    server.serve_forever()
