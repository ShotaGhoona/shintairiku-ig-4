"""
Notification Service
Slack通知などの外部通知サービス
"""

import json
import requests
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """通知サービスクラス"""
    
    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
    async def send_account_insights_result(self, result) -> bool:
        """アカウントインサイト収集結果をSlackに送信"""
        
        if not self.slack_webhook_url:
            logger.warning("SLACK_WEBHOOK_URL not configured, skipping notification")
            return False
            
        try:
            success_rate = (result.successful_accounts / result.total_accounts * 100) if result.total_accounts > 0 else 0
            duration = (result.completed_at - result.started_at).total_seconds()
            
            # メッセージ作成
            color = "good" if success_rate >= 80 else "warning" if success_rate >= 50 else "danger"
            
            message = {
                "text": "📊 Instagram Account Insights Collection Completed",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "Success Rate",
                                "value": f"{success_rate:.1f}% ({result.successful_accounts}/{result.total_accounts})",
                                "short": True
                            },
                            {
                                "title": "Duration",
                                "value": f"{duration:.1f}s",
                                "short": True
                            },
                            {
                                "title": "Stats Created",
                                "value": str(result.stats_created),
                                "short": True
                            },
                            {
                                "title": "Stats Updated", 
                                "value": str(result.stats_updated),
                                "short": True
                            },
                            {
                                "title": "API Calls",
                                "value": str(result.api_calls_made),
                                "short": True
                            },
                            {
                                "title": "Target Date",
                                "value": result.target_date.strftime("%Y-%m-%d"),
                                "short": True
                            }
                        ],
                        "footer": "Instagram Analysis Bot",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            # エラーがある場合は追加
            if result.errors:
                error_field = {
                    "title": f"Errors ({len(result.errors)})",
                    "value": "\n".join(result.errors[:3]) + ("..." if len(result.errors) > 3 else ""),
                    "short": False
                }
                message["attachments"][0]["fields"].append(error_field)
            
            response = requests.post(self.slack_webhook_url, json=message, timeout=30)
            response.raise_for_status()
            
            logger.info("Account insights result notification sent to Slack")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def send_new_posts_notification(self, result) -> bool:
        """新規投稿検出結果をSlackに送信"""
        
        if not self.slack_webhook_url:
            logger.warning("SLACK_WEBHOOK_URL not configured, skipping notification")
            return False
            
        try:
            duration = (result.completed_at - result.started_at).total_seconds()
            
            # メッセージ作成
            color = "good" if result.new_posts_found > 0 else "#439FE0"
            
            message = {
                "text": f"🆕 New Instagram Posts {'Detected!' if result.new_posts_found > 0 else 'Check Completed'}",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "New Posts Found",
                                "value": str(result.new_posts_found),
                                "short": True
                            },
                            {
                                "title": "Posts Saved",
                                "value": str(result.new_posts_saved),
                                "short": True
                            },
                            {
                                "title": "Insights Collected", 
                                "value": str(result.insights_collected),
                                "short": True
                            },
                            {
                                "title": "Accounts Checked",
                                "value": f"{result.successful_accounts}/{result.total_accounts}",
                                "short": True
                            },
                            {
                                "title": "API Calls",
                                "value": str(result.api_calls_made),
                                "short": True
                            },
                            {
                                "title": "Duration",
                                "value": f"{duration:.1f}s",
                                "short": True
                            }
                        ],
                        "footer": "Instagram Posts Monitor",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            # 新規投稿詳細を追加（最初の5件まで）
            if result.new_posts_details:
                posts_summary = []
                for post in result.new_posts_details[:5]:
                    emoji = "📊" if post['insights_collected'] else "❌"
                    posts_summary.append(f"@{post['account_username']}: {post['media_type']} {emoji}")
                
                if len(result.new_posts_details) > 5:
                    posts_summary.append(f"... and {len(result.new_posts_details) - 5} more")
                
                posts_field = {
                    "title": "New Posts Details",
                    "value": "\n".join(posts_summary),
                    "short": False
                }
                message["attachments"][0]["fields"].append(posts_field)
            
            response = requests.post(self.slack_webhook_url, json=message, timeout=30)
            response.raise_for_status()
            
            logger.info("New posts notification sent to Slack")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def send_failure_notification(self, workflow: str, run_id: str, message: str) -> bool:
        """失敗通知をSlackに送信"""
        
        if not self.slack_webhook_url:
            logger.warning("SLACK_WEBHOOK_URL not configured, skipping notification")
            return False
            
        try:
            slack_message = {
                "text": "❌ GitHub Actions Workflow Failed",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {
                                "title": "Workflow",
                                "value": workflow,
                                "short": True
                            },
                            {
                                "title": "Run ID",
                                "value": run_id,
                                "short": True
                            },
                            {
                                "title": "Error Message",
                                "value": message,
                                "short": False
                            }
                        ],
                        "footer": "GitHub Actions",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook_url, json=slack_message, timeout=30)
            response.raise_for_status()
            
            logger.info("Failure notification sent to Slack")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")
            return False

# CLI用エントリーポイント
def main():
    parser = argparse.ArgumentParser(description='Send notification via Slack')
    parser.add_argument('--type', choices=['failure'], required=True, help='Notification type')
    parser.add_argument('--workflow', required=True, help='Workflow name')
    parser.add_argument('--run-id', required=True, help='GitHub Actions run ID')
    parser.add_argument('--message', required=True, help='Error message')
    
    args = parser.parse_args()
    
    notification = NotificationService()
    
    if args.type == 'failure':
        success = notification.send_failure_notification(
            workflow=args.workflow,
            run_id=args.run_id,
            message=args.message
        )
        
        if success:
            print("Notification sent successfully")
            return 0
        else:
            print("Failed to send notification")
            return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)