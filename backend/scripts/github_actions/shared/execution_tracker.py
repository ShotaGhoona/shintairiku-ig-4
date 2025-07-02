"""
Execution Tracker
実行状態管理
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import logging

class ExecutionTracker:
    """実行状態追跡クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state_file = Path(__file__).parent.parent.parent.parent / "data" / "execution_state" / "new_posts_last_execution.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_last_execution_time(self) -> Optional[datetime]:
        """前回実行時刻取得"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                last_time_str = state.get('last_execution_time')
                if last_time_str:
                    dt = datetime.fromisoformat(last_time_str)
                    # naive datetimeの場合はUTCとして扱う
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to load execution state: {e}")
            return None
    
    def update_last_execution_time(self, execution_time: datetime):
        """実行時刻更新"""
        try:
            # タイムゾーン情報を含めて保存
            if execution_time.tzinfo is None:
                execution_time = execution_time.replace(tzinfo=timezone.utc)
            
            current_time = datetime.now(timezone.utc)
            
            state = {
                'last_execution_time': execution_time.isoformat(),
                'updated_at': current_time.isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"Execution state updated: {execution_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to update execution state: {e}")