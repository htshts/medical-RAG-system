"""
简化版后端服务（无需外部依赖）
使用 Python 内置模块实现，可直接运行
"""

import json
import time
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 内存存储（模拟数据）
patients = {}
records = {}


def init_mock_data():
    """初始化模拟数据"""
    # 生成 10 名模拟患者
    for i in range(1, 11):
        patient_id = f"P{i:05d}"
        patients[patient_id] = {
            "patient_id": patient_id,
            "name": f"患者{patient_id}",
            "gender": "男" if i % 2 == 0 else "女",
            "age": 30 + i,
            "admissions": [
                {"admission_date": "2024-01-10", "diagnosis": "急性心肌梗死"}
            ]
        }
        
        # 生成模拟病历记录
        record_id = f"{patient_id}_REC_001"
        records[record_id] = {
            "record_id": record_id,
            "patient_id": patient_id,
            "record_type": "入院记录",
            "content": f"""
入院记录
患者 {patient_id}，因"胸痛3天"于2024年1月10日入院。

【主诉】
胸痛3天。

【现病史】
患者于2024年1月7日无明显诱因出现胸痛，伴有恶心、呕吐，无发热、咳嗽等症状。
入院后查心电图提示：窦性心律，心肌缺血表现。
血常规：WBC 10.0×10^9/L，NE% 80%。
生化：cTnI 升高，CK-MB 升高。

【既往史】
高血压病史10年，最高160/100 mmHg，目前口服阿司匹林肠溶片控制血压。
糖尿病病史5年，目前皮下注射胰岛素控制血糖。

【体格检查】
T: 36.5℃
P: 78次/分
R: 18次/分
BP: 145/95 mmHg

【初步诊断】
1. 急性心肌梗死
2. 高血压
3. 2型糖尿病

【诊疗计划】
1. 完善相关检查：血常规、生化全套、凝血功能、心电图、超声心动图等。
2. 给予阿司匹林肠溶片、氯吡格雷片等药物治疗。
3. 密切观察生命体征变化。
4. 向患者及家属告知病情，签署知情同意书。
""",
            "admission_date": "2024-01-10",
            "diagnosis": "急性心肌梗死",
            "medications": ["阿司匹林肠溶片", "氯吡格雷片"]
        }
    
    print(f"[OK] 模拟数据初始化完成：{len(patients)} 名患者，{len(records)} 条记录")


def query_rewrite(query: str) -> dict:
    """Query 改写（简化版）"""
    # 简单意图识别
    intent = "综合查"
    if "患者" in query or "P000" in query:
        intent = "按患者查"
    elif "诊断" in query or "疾病" in query:
        intent = "按疾病查"
    elif "时间" in query or "日期" in query:
        intent = "按时间查"
    
    return {
        "original_query": query,
        "rewritten_query": query,
        "intent": intent,
        "entities": [],
        "time_expressions": []
    }


def hybrid_search(query: str, patient_id: str = None) -> list:
    """混合检索（简化版 - 关键词匹配）"""
    results = []
    
    for record_id, record in records.items():
        # 如果指定了患者 ID，则只搜索该患者的记录
        if patient_id and record["patient_id"] != patient_id:
            continue
        
        content = record.get("content", "")
        
        # 简单关键词匹配
        if query.lower() in content.lower():
            results.append({
                "record_id": record_id,
                "patient_id": record["patient_id"],
                "content": content[:500],
                "score": 1.0,
                "source": "keyword_match"
            })
    
    return results


def generate_summary(patient_id: str) -> dict:
    """生成转院摘要（简化版）"""
    # 获取患者信息
    patient = patients.get(patient_id)
    if not patient:
        return {"error": f"患者不存在: {patient_id}"}
    
    # 获取患者病历记录
    patient_records = [r for r in records.values() if r["patient_id"] == patient_id]
    
    # 生成简化版摘要
    summary = {
        "patient_summary": {
            "chief_complaint": "胸痛3天",
            "diagnosis": [
                {"name": "急性心肌梗死", "icd_code": "I21.0", "confidence": 0.95}
            ],
            "key_events": [
                {"time": "2024-01-10T08:00:00", "event": "入院", "details": "患者因胸痛入院"},
                {"time": "2024-01-12T14:00:00", "event": "冠脉造影", "details": "提示前降支狭窄90%"}
            ],
            "medications": [
                {"name": "阿司匹林肠溶片", "dosage": "100mg", "frequency": "每日1次", "start_date": "2024-01-10"}
            ],
            "examinations": [
                {"name": "心电图", "date": "2024-01-10", "result": "心肌缺血表现"}
            ],
            "transfer_recommendation": "建议转心血管内科CCU进一步治疗"
        },
        "information_completeness": {
            "chief_complaint": True,
            "diagnosis": True,
            "key_events": True,
            "medications": True,
            "examinations": True
        },
        "missing_information": []
    }
    
    return summary


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == "/":
            self._send_json({
                "app_name": "Medical RAG System (Demo)",
                "version": "1.0.0",
                "status": "running",
                "docs": "/docs (请用浏览器访问前端界面)"
            })
            
        elif path == "/api/patient/search":
            keyword = query_params.get("keyword", [""])[0]
            results = []
            for p in patients.values():
                if keyword.lower() in p["patient_id"].lower() or keyword in p["name"]:
                    results.append(p)
            self._send_json({"patients": results[:10], "total": len(results)})
            
        elif path.startswith("/api/patient/"):
            patient_id = path.split("/")[-1]
            patient = patients.get(patient_id)
            if patient:
                self._send_json(patient)
            else:
                self._send_error(404, f"患者不存在: {patient_id}")
                
        elif path.startswith("/api/summary/"):
            patient_id = path.split("/")[-1]
            summary = generate_summary(patient_id)
            self._send_json(summary)
            
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == "/api/query/search":
            query = data.get("query", "")
            patient_id = data.get("patient_id")
            
            # Query 改写
            rewritten = query_rewrite(query)
            
            # 混合检索
            start_time = time.time()
            results = hybrid_search(query, patient_id)
            elapsed_time = (time.time() - start_time) * 1000
            
            self._send_json({
                "query": query,
                "rewritten_query": rewritten,
                "results": results,
                "total": len(results),
                "time_ms": elapsed_time,
                "trace_id": f"trace_{int(time.time() * 1000)}"
            })
            
        else:
            self._send_error(404, "Endpoint not found")
    
    def _send_json(self, data: dict, status_code: int = 200):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def _send_error(self, status_code: int, message: str):
        """发送错误响应"""
        self._send_json({"error": message}, status_code)
    
    def log_message(self, format, *args):
        """禁用默认日志"""
        pass


def run_server(host: str = "localhost", port: int = 8000):
    """启动 HTTP 服务器"""
    server = HTTPServer((host, port), RequestHandler)
    
    print("=" * 60)
    print("医疗RAG系统 - 简化版演示服务")
    print("=" * 60)
    print(f"[OK] 服务器启动成功！")
    print(f"[ACCESS] 访问地址：http://{host}:{port}")
    print(f"[API] 可用接口：")
    print(f"   - GET  /api/patient/search?keyword=xxx  (搜索患者)")
    print(f"   - GET  /api/patient/{{patient_id}}  (获取患者信息)")
    print(f"   - POST /api/query/search  (检索查询)")
    print(f"   - GET  /api/summary/{{patient_id}}  (生成转院摘要)")
    print(f"\n按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ 服务器已停止")
        server.shutdown()


if __name__ == "__main__":
    # 初始化模拟数据
    init_mock_data()
    
    # 启动服务器
    run_server(port=8000)
