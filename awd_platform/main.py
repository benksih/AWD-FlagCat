# main.py
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File
import shutil
from pathlib import Path
from fastapi import WebSocket, WebSocketDisconnect # <--- 新增导入
from .websocket_manager import manager # <--- 新增导入
from .models import SystemConfig, Target, UpdateTargetsRequest
from .state import app_state
from . import attack_logic # <--- 新增导入

# --- 应用生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    print("[*] [SYSTEM] 应用启动...")
    yield
    # 应用关闭时执行
    print("[*] [SYSTEM] 应用正在关闭...")
    if app_state.attack_running:
        print("[*] [SYSTEM] 正在停止攻击循环...")
        app_state.attack_running = False
        if app_state.attack_task:
            app_state.attack_task.cancel() # 取消任务
    print("[*] [SYSTEM] 清理完成，应用已关闭。")


app = FastAPI(
    title="AWD自动攻击平台后端",
    description="提供配置管理、目标管理和攻击控制API",
    version="1.0.0",
    lifespan=lifespan # <--- 注册生命周期函数
)
origins = [
    "http://localhost",
    "http://localhost:1420",  # Vite开发服务器的默认地址
    "tauri://localhost",      # Tauri应用的协议
    "http://tauri.localhost", # Tauri应用的备用协议
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # 允许访问的源列表
    allow_credentials=True,    # 允许携带cookie
    allow_methods=["*"],       # 允许所有HTTP方法 (GET, POST, etc.)
    allow_headers=["*"],       # 允许所有HTTP请求头
)
@app.get("/")
def read_root():
    return {"message": "欢迎使用AWD自动攻击平台后端服务"}

# --- 系统配置模块 (无变化) ---
@app.post("/api/config", response_model=SystemConfig, tags=["Config"])
def update_system_config(config: SystemConfig):
    app_state.update_config(config)
    return app_state.get_config()

@app.get("/api/config", response_model=SystemConfig, tags=["Config"])
def get_system_config():
    return app_state.get_config()

# --- 目标管理模块 (无变化) ---
@app.post("/api/targets", status_code=status.HTTP_201_CREATED, tags=["Targets"])
def update_targets(request: UpdateTargetsRequest):
    if not request.ips:
        raise HTTPException(status_code=400, detail="IP列表不能为空")
    unique_ips = sorted(list(set(request.ips)))
    app_state.update_targets(unique_ips)
    return {"message": f"成功更新 {len(unique_ips)} 个目标。"}

@app.get("/api/targets", response_model=List[Target], tags=["Targets"])
def get_all_targets():
    return app_state.get_all_targets()

# --- 攻击控制模块 (核心新增) ---
@app.post("/api/control/start", tags=["Control"])
async def start_attack():
    """启动自动化攻击循环"""
    if app_state.attack_running:
        raise HTTPException(status_code=400, detail="攻击已经在运行中")
    
    app_state.attack_running = True
    # 在后台创建一个任务来运行攻击循环
    app_state.attack_task = asyncio.create_task(attack_logic.main_attack_loop())
    
    return {"message": "攻击已启动"}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 等待客户端消息 (虽然我们目前不处理客户端发来的消息，但这个循环是保持连接所必需的)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[*] [SYSTEM] 一个前端客户端已断开连接。")

@app.post("/api/control/stop", tags=["Control"])
async def stop_attack():
    """停止自动化攻击循环"""
    if not app_state.attack_running:
        raise HTTPException(status_code=400, detail="攻击当前未运行")
    
    app_state.attack_running = False
    if app_state.attack_task:
        app_state.attack_task.cancel()
        # 等待任务真正被取消
        try:
            await app_state.attack_task
        except asyncio.CancelledError:
            print("[*] [SYSTEM] 任务成功取消")
            
    app_state.attack_task = None
    return {"message": "攻击已停止"}

EXPLOITS_DIR = Path(__file__).parent / "exploits"

@app.post("/api/exploits/upload", tags=["Exploits"])
async def upload_exploit(file: UploadFile = File(...)):
    """接收并保存上传的攻击脚本"""
    # 确保exploits目录存在
    EXPLOITS_DIR.mkdir(exist_ok=True)
    
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="只能上传.py文件")

    file_path = EXPLOITS_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "message": "脚本上传成功"}

@app.get("/api/exploits", response_model=List[str], tags=["Exploits"])
def get_exploits():
    """获取所有已上传的攻击脚本文件名"""
    if not EXPLOITS_DIR.exists():
        return []
    
    # .pyc 是Python编译的缓存文件，我们需要过滤掉
    py_files = [f.name for f in EXPLOITS_DIR.glob("*.py") if f.name != "__init__.py"]
    return py_files
