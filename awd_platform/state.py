# state.py
from typing import List, Dict
from threading import Lock
from .models import SystemConfig, Target, TargetStatus

class AppState:
    """
    一个单例类，用于在内存中存储和管理整个应用的共享状态。
    使用线程锁来保证多线程（或异步任务）访问时的数据安全。
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            with self._lock:
                self.config = SystemConfig()
                self.targets: Dict[str, Target] = {}
                self.next_target_id = 1
                self.attack_running = False
                # 新增一个字段来保存后台攻击任务的引用
                self.attack_task: Optional[asyncio.Task] = None 
                self.initialized = True

    def update_config(self, new_config: SystemConfig):
        with self._lock:
            self.config = new_config

    def get_config(self) -> SystemConfig:
        with self._lock:
            return self.config

    def update_targets(self, ips: List[str]):
        with self._lock:
            self.targets.clear()
            self.next_target_id = 1
            for ip in ips:
                if ip not in self.targets:
                    new_target = Target(id=self.next_target_id, ip=ip)
                    self.targets[ip] = new_target
                    self.next_target_id += 1
    
    def get_all_targets(self) -> List[Target]:
        with self._lock:
            return list(self.targets.values())

# 创建全局状态的单例
app_state = AppState()