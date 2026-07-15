"""
简化版演示服务 - 可直接运行（支持前端）
使用 Python 内置模块，无需任何外部依赖
运行方法：python demo_server_simple.py
"""

import json
import time
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ============================================
# 配置
# ============================================

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'frontend')

# MIME 类型映射
MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
}

# ============================================
# 内存数据存储
# ============================================

patients = {}
records = {}

def init_mock_data():
    """初始化模拟数据"""
    diseases = ["糖尿病", "高血压", "冠心病", "脑梗塞", "肺炎", "胃溃疡", "支气管哮喘", "类风湿关节炎"]
    departments = ["心内科", "内分泌科", "神经内科", "呼吸内科", "消化内科", "骨科", "普外科"]
    
    for i in range(1, 21):
        pid = f"P{i:05d}"
        age = 30 + i * 2
        gender = "Male" if i % 2 == 0 else "Female"
        
        patients[pid] = {
            "patient_id": pid,
            "name": f"患者{i}",
            "gender": gender,
            "age": age,
            "phone": f"138{10000000 + i}",
            "address": f"北京市海淀区{i}号",
            "admissions": [{"date": "2024-01-10", "department": departments[i % len(departments)], "diagnosis": diseases[i % len(diseases)]}]
        }
        
        # 创建多条就诊记录
        for j in range(1, 4):
            rid = f"{pid}_REC_{j:03d}"
            records[rid] = {
                "record_id": rid,
                "patient_id": pid,
                "record_type": "门诊病历" if j == 1 else "住院记录",
                "department": departments[(i + j) % len(departments)],
                "visit_time": f"2024-{j:02d}-{10 + j:02d}T{9 + j}:00:00",
                "doctor": f"医生{j}",
                "content": f"患者{pid}于{2024}年{j}月就诊，主诉：{diseases[i % len(diseases)]}相关症状。"
                           f"现病史：患者既往有{diseases[(i+1) % len(diseases)]}病史{j}年。"
                           f"体格检查：血压{120 + i}/{80 + i}mmHg，心率{j*10}次/分。"
                           f"诊断：{diseases[i % len(diseases)]}。"
                           f"治疗方案：药物治疗，建议定期复查。",
                "diagnosis": diseases[i % len(diseases)],
                "medications": [f"药物A{j}", f"药物B{j}"]
            }
    
    print(f"[OK] Mock data initialized: {len(patients)} patients, {len(records)} records")

# ============================================
# RAG 检索模块（简化版）
# ============================================

def query_rewrite(query):
    """Query 改写（简化版）"""
    intent = "comprehensive_search"
    if "患者" in query or "P000" in query:
        intent = "search_by_patient"
    elif "诊断" in query or "疾病" in query:
        intent = "search_by_disease"
    
    return {
        "original_query": query,
        "rewritten_query": query,
        "intent": intent,
        "entities": []
    }


def hybrid_search(query, patient_id=None, top_k=10):
    """混合检索（简化版 - 关键词匹配）"""
    results = []
    query_lower = query.lower()
    
    for rid, record in records.items():
        if patient_id and record["patient_id"] != patient_id:
            continue
        
        content = record.get("content", "")
        title = record.get("record_type", "")
        
        # 简单相关性评分
        score = 0.0
        if query in content:
            score = 0.9
        elif any(word in content for word in query.split()):
            score = 0.6
        
        if score > 0:
            results.append({
                "document": {
                    "record_id": rid,
                    "patient_id": record["patient_id"],
                    "title": title,
                    "content": content[:500],
                    "department": record.get("department", ""),
                    "record_type": record.get("record_type", ""),
                    "visit_time": record.get("visit_time", "")
                },
                "score": score,
                "source": "keyword_match"
            })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ============================================
# HTTP 请求处理
# ============================================

class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # 静态文件服务
        if path == "/" or path.endswith(".html"):
            self._serve_static(path)
            return
        
        if "." in path.split("/")[-1]:  # 有文件扩展名
            self._serve_static(path)
            return
        
        # API 端点
        if path == "/api/health" or path == "/health":
            self._send_json({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0-demo"
            })
            
        elif path == "/api/v1/query/suggest":
            query = params.get("query", [""])[0]
            suggestions = []
            if len(query) >= 2:
                suggestions = [
                    {"text": f"{query} 在2024年1月", "score": 0.9},
                    {"text": f"{query} 的诊断记录", "score": 0.85},
                    {"text": f"患者{query}的用药情况", "score": 0.8},
                ]
            self._send_json({"suggestions": suggestions})
            
        elif path == "/api/v1/patient/search":
            keyword = params.get("keyword", [""])[0]
            results = []
            for p in patients.values():
                if keyword.lower() in p["patient_id"].lower() or keyword in p["name"]:
                    results.append(p)
            self._send_json({"patients": results[:10], "total": len(results)})
            
        elif path.startswith("/api/v1/patient/"):
            pid = path.split("/")[-1]
            patient = patients.get(pid)
            if patient:
                # 获取患者的时间轴
                timeline = []
                for rid, record in records.items():
                    if record["patient_id"] == pid:
                        timeline.append({
                            "date": record.get("visit_time", ""),
                            "type": record.get("record_type", ""),
                            "department": record.get("department", ""),
                            "description": record.get("content", "")[:200]
                        })
                
                response = {
                    "patient": patient,
                    "timeline": sorted(timeline, key=lambda x: x["date"]),
                    "entities": {
                        "diseases": [{"name": patient["admissions"][0]["diagnosis"]}],
                        "symptoms": [{"name": "胸痛"}],
                        "medications": [{"name": "阿司匹林"}]
                    }
                }
                self._send_json(response)
            else:
                self._send_error(404, f"Patient not found: {pid}")
                
        elif path.startswith("/api/v1/summary/"):
            parts = path.split("/")
            pid = parts[-2] if len(parts) > 4 else parts[-1]
            patient = patients.get(pid)
            if patient:
                summary = {
                    "summary_id": f"SUM_{pid}_001",
                    "patient_id": pid,
                    "summary_type": "transfer",
                    "sections": {
                        "chief_complaint": {
                            "title": "主诉",
                            "text": "患者因胸痛3天入院"
                        },
                        "history": {
                            "title": "现病史",
                            "text": "患者3天前无明显诱因出现胸痛，位于胸骨后，呈压榨样疼痛，伴出汗，持续约10分钟，休息后缓解。既往有高血压病史10年，糖尿病病史5年。"
                        },
                        "examination": {
                            "title": "体格检查",
                            "text": "BP 145/95mmHg，HR 88次/分，律齐，各瓣膜听诊区未闻及病理性杂音。双肺呼吸音清，未闻及干湿性啰音。"
                        },
                        "diagnosis": {
                            "title": "诊断",
                            "text": "1. 急性ST段抬高型心肌梗死（前壁）\n2. 高血压3级（很高危）\n3. 2型糖尿病"
                        },
                        "treatment": {
                            "title": "治疗方案",
                            "text": "1. 抗血小板聚集：阿司匹林100mg qd + 氯吡格雷75mg qd\n2. 调脂稳定斑块：阿托伐他汀20mg qn\n3. 降压：ACEI类药物\n4. 降糖：二甲双胍0.5g tid"
                        }
                    },
                    "entities": {
                        "diseases": [{"name": "急性ST段抬高型心肌梗死"}],
                        "symptoms": [{"name": "胸痛"}, {"name": "出汗"}],
                        "medications": [{"name": "阿司匹林"}, {"name": "氯吡格雷"}]
                    },
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "model": "demo-model",
                        "processing_time_ms": 1250
                    }
                }
                self._send_json(summary)
            else:
                self._send_error(404, f"Patient not found: {pid}")
                
        else:
            self._send_error(404, f"Endpoint not found: {path}")
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == "/api/v1/query/search":
            query = data.get("query", "")
            patient_id = data.get("patient_id")
            top_k = data.get("top_k", 10)
            enable_time_align = data.get("enable_time_align", True)
            
            # Query 改写
            rewritten = query_rewrite(query)
            
            # 混合检索
            start_time = time.time()
            results = hybrid_search(query, patient_id, top_k)
            elapsed = (time.time() - start_time) * 1000
            
            self._send_json({
                "query": query,
                "query_info": {
                    "processed_query": rewritten["rewritten_query"],
                    "intent": rewritten["intent"]
                },
                "results": results,
                "total": len(results),
                "time_ms": elapsed,
                "trace_id": f"trace_{int(time.time() * 1000)}"
            })
            
        elif path == "/api/v1/summary/generate":
            patient_id = data.get("patient_id")
            summary_type = data.get("summary_type", "transfer")
            sections = data.get("include_sections", [])
            
            # 模拟生成延迟
            time.sleep(1)
            
            summary = {
                "summary_id": f"SUM_{patient_id}_001",
                "patient_id": patient_id,
                "summary_type": summary_type,
                "status": "completed",
                "sections": {
                    "chief_complaint": {"title": "主诉", "text": "患者因胸痛3天入院"},
                    "history": {"title": "现病史", "text": "患者3天前无明显诱因出现胸痛..."},
                    "diagnosis": {"title": "诊断", "text": "1. 急性ST段抬高型心肌梗死\n2. 高血压"},
                    "treatment": {"title": "治疗方案", "text": "1. 抗血小板聚集\n2. 调脂稳定斑块"}
                },
                "entities": {
                    "diseases": [{"name": "急性ST段抬高型心肌梗死"}],
                    "medications": [{"name": "阿司匹林"}]
                },
                "created_at": datetime.now().isoformat()
            }
            
            self._send_json(summary)
            
        else:
            self._send_error(404, f"Endpoint not found: {path}")
    
    def _serve_static(self, path):
        """提供静态文件服务"""
        # 构建文件路径
        if path == "/":
            file_path = os.path.join(FRONTEND_DIR, "index.html")
        else:
            # 移除开头的 /
            relative_path = path.lstrip("/")
            file_path = os.path.join(FRONTEND_DIR, relative_path)
        
        # 安全检查：确保文件路径在 FRONTEND_DIR 内
        file_path = os.path.realpath(file_path)
        if not file_path.startswith(os.path.realpath(FRONTEND_DIR)):
            self._send_error(403, "Forbidden")
            return
        
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            # 如果文件不存在，返回 index.html（SPA 模式）
            file_path = os.path.join(FRONTEND_DIR, "index.html")
        
        if not os.path.isfile(file_path):
            self._send_error(404, "File not found")
            return
        
        # 获取 MIME 类型
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = MIME_TYPES.get(ext, 'application/octet-stream')
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            self._send_error(500, f"Error reading file: {str(e)}")
    
    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def _send_error(self, status, message):
        """发送错误响应"""
        self._send_json({"detail": message}, status)
    
    def do_OPTIONS(self):
        """处理 OPTIONS 请求（CORS）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")


# ============================================
# 主函数
# ============================================

def run_server(host="localhost", port=8000):
    """启动 HTTP 服务器"""
    server = HTTPServer((host, port), RequestHandler)
    
    print("=" * 60)
    print("Medical RAG System - Simple Demo Server (With Frontend)")
    print("=" * 60)
    print(f"[OK] Server started successfully!")
    print(f"[ACCESS] http://{host}:{port}")
    print(f"[FRONTEND] {FRONTEND_DIR}")
    print(f"\nAPI Endpoints:")
    print(f"   GET  /api/v1/query/suggest?query=xxx")
    print(f"   POST /api/v1/query/search")
    print(f"   GET  /api/v1/patient/{{patient_id}}")
    print(f"   GET  /api/v1/patient/search?keyword=xxx")
    print(f"   POST /api/v1/summary/generate")
    print(f"   GET  /api/v1/summary/{{patient_id}}/{{summary_id}}")
    print(f"\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped")
        server.shutdown()


if __name__ == "__main__":
    init_mock_data()
    run_server(port=8000)
