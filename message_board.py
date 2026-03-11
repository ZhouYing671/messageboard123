#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json, os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DATA_FILE = 'messages.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f: json.dump([], f)

def load(): return json.load(open(DATA_FILE))
def save(d): json.dump(d, open(DATA_FILE, 'w'), ensure_ascii=False, indent=2)

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>留言板</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px}.container{max-width:800px;margin:0 auto;background:#fff;border-radius:20px;overflow:hidden}.header{background:linear-gradient(135deg,#4CAF50,#45a049);color:#fff;padding:30px;text-align:center}.header h1{font-size:28px}.input-section{padding:30px}textarea{width:100%;padding:15px;border:2px solid #e0e0e0;border-radius:10px;font-size:16px;min-height:120px}button{background:linear-gradient(135deg,#4CAF50,#45a049);color:#fff;border:none;padding:12px 40px;font-size:16px;border-radius:25px;cursor:pointer;margin-top:15px}.stats{padding:20px 30px;background:#f9f9f9;display:flex;justify-content:space-between}.message-list{padding:20px 30px;max-height:500px;overflow-y:auto}.message-item{background:#f9f9f9;border-radius:12px;padding:20px;margin-bottom:15px;border-left:4px solid #4CAF50}.name{color:#4CAF50;font-weight:bold}.content{color:#333;font-size:16px;line-height:1.6;margin:8px 0}.time{color:#999;font-size:12px}.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);justify-content:center;align-items:center;z-index:1000}.modal.show{display:flex}.modal-content{background:#fff;border-radius:20px;padding:30px;max-width:400px;width:90%;text-align:center}input{width:100%;padding:12px;border:2px solid #e0e0e0;border-radius:10px;font-size:16px;margin:20px 0}</style></head><body><div class="container"><div class="header"><h1>📝 多人协作留言板</h1><p>多人同时在线留言</p></div><div class="input-section"><textarea id="msg" placeholder="请输入内容..."></textarea><button onclick="showModal()">提交留言</button></div><div class="stats"><div>共 <strong id="count">0</strong> 条留言</div><button onclick="exportData()" style="background:#2196F3;padding:10px 25px;font-size:14px">导出Excel</button></div><div class="message-list" id="list"></div></div><div class="modal" id="modal"><div class="modal-content"><h2>请输入姓名</h2><input type="text" id="name" placeholder="您的姓名"><div><button onclick="hideModal()" style="background:#999;margin-right:10px">取消</button><button onclick="submit()">确认</button></div></div></div><script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script><script>let cur='';async function load(){const r=await fetch('/api/messages'),m=await r.json();document.getElementById('count').textContent=m.length;document.getElementById('list').innerHTML=m.map(x=>`<div class="message-item"><div class="name">👤 ${x.name}</div><div class="content">${x.content}</div><div class="time">🕐 ${new Date(x.time).toLocaleString('zh-CN')}</div></div>`).join('')}function showModal(){const c=document.getElementById('msg').value.trim();if(!c){alert('请输入内容');return}cur=c;document.getElementById('modal').classList.add('show')}function hideModal(){document.getElementById('modal').classList.remove('show')}async function submit(){const n=document.getElementById('name').value.trim();if(!n){alert('请输入姓名');return}await fetch('/api/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,content:cur})});hideModal();document.getElementById('msg').value='';load()}async function exportData(){const r=await fetch('/api/messages'),m=await r.json(),d=m.map(x=>({'姓名':x.name,'内容':x.content,'时间':new Date(x.time).toLocaleString('zh-CN')})),ws=XLSX.utils.json_to_sheet(d),wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,ws,'留言');XLSX.writeFile(wb,'留言记录.xlsx')}load();setInterval(load,3000)</script></body></html>"""

@app.route('/')
def index(): return render_template_string(HTML)
@app.route('/api/messages')
def get(): return jsonify(sorted(load(), key=lambda x: x['time'], reverse=True))
@app.route('/api/add', methods=['POST'])
def add():
    d = request.get_json()
    m = load()
    m.append({'name': d['name'], 'content': d['content'], 'time': datetime.now().isoformat()})
    save(m)
    return jsonify({'ok': True})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
