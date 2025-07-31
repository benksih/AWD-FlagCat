# models.py
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import time

class TargetStatus(str, Enum):
    """目标状态的枚举类型"""
    PENDING = "PENDING"
    ATTACKING = "ATTACKING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ERROR = "ERROR"

class SystemConfig(BaseModel):
    """系统配置模型"""
    submit_url: str = "http://challenge.host/api/submit"
    token: str = "YOUR_DEFAULT_TOKEN"
    selected_exploit: str = "example_exp.py"
    concurrency: int = Field(10, ge=1, le=100) # 并发数限制在1到100之间
    round_interval: int = Field(60, ge=10) # 轮询间隔, 单位秒, 不小于10秒

class Target(BaseModel):
    """单个目标的详细模型"""
    id: int
    ip: str
    status: TargetStatus = TargetStatus.PENDING
    last_attack_time: Optional[float] = None
    success_flags_count: int = 0
    log: List[str] = []

class UpdateTargetsRequest(BaseModel):
    """更新目标列表的请求体模型"""
    ips: List[str]

class LogEntry(BaseModel):
    """日志条目模型，用于WebSocket推送"""
    timestamp: float = Field(default_factory=time.time)
    level: str # INFO, SUCCESS, ERROR
    target_ip: Optional[str] = None
    message: str
class HttpParam(BaseModel):
    """单个HTTP参数的模型"""
    key: str = ""
    value: str = ""

class SimpleHttpAttack(BaseModel):
    """可视化HTTP攻击配置的模型"""
    method: str = "GET"
    # port: int = 80  # <--- 删除这一行
    path: str = "/"
    params: List[HttpParam] = [] 
    data: List[HttpParam] = []   
    flag_regex: str = "flag{[a-zA-Z0-9-_]+}"

class SystemConfig(BaseModel):
    """系统配置模型 - 最终版"""
    submit_url: str = "http://challenge.host/api/submit"
    token: str = "YOUR_DEFAULT_TOKEN"
    concurrency: int = Field(10, ge=1, le=100)
    round_interval: int = Field(60, ge=10)
    
    # --- 新增字段 ---
    attack_mode: str = "python_script" # 'python_script' 或 'http_request'
    selected_exploit: str = "example_exp.py"
    http_attack_config: SimpleHttpAttack = Field(default_factory=SimpleHttpAttack)
