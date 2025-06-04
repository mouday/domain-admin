import requests
import schedule
import time
import json
from notifier import Notifier  # 确保notifier.py在相同目录

class DomainMonitor:
    def __init__(self):
        # 更新为本地Python接口
        self.check_api = "http://localhost:5000/check"
        self.urls = [
            "https://login.jpgoodbuy.com",
            "qbt.jp",
            "q.jpgoodbuy.com",
            "www.jpgoodbuy.com",
            "jpgoodbuy.com",
            "api.jpkix.com"
        ]
        self.timeout = 10  # 请求超时时间(秒)
        self.retries = 2  # 失败重试次数

    def _check_single_url(self, url: str) -> dict:
        """执行单个URL检测"""
        for _ in range(self.retries):
            try:
                resp = requests.get(
                    self.check_api,
                    params={"url": url},
                    timeout=self.timeout
                )

                if resp.status_code == 200:
                    return resp.json()
                else:
                    print(f"接口异常 - URL: {url} 状态码: {resp.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"请求失败 - URL: {url} 错误: {str(e)}")
            except json.JSONDecodeError:
                print(f"响应解析失败 - URL: {url}")

            time.sleep(1)  # 失败后等待1秒重试

        return {"code": 500, "msg": "检测失败"}

    def batch_check(self):
        """批量检测所有URL"""
        print(f"\n开始检测任务 {time.strftime('%Y-%m-%d %H:%M:%S')}")

        for url in self.urls:
            result = self._check_single_url(url)

            if result.get("code") == 202:
                # 发送告警邮件
                Notifier.war_mall(
                    subject=f"域名封禁告警 - {url}",
                    content=f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"违规域名: {url}\n"
                            f"拦截原因: {result.get('msg', '未知原因')}"
                )
                print(f"已发送告警: {url}")
            elif result.get("code") == 200:
                print(f"域名正常: {url}")
            else:
                print(f"检测异常: {url} - {result.get('msg', '未知错误')}")


def main():
    monitor = DomainMonitor()

    # 注册定时任务
    schedule.every(15).minutes.do(monitor.batch_check)

    # 立即执行首次检测
    monitor.batch_check()

    # 保持定时任务运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次任务


if __name__ == "__main__":
    main()