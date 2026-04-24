"""
HTTP检查器
"""

import requests
import time
import urllib3
from typing import Any, Dict, Optional
from urllib.parse import urljoin

# 禁用SSL警告（因verify=False会产生InsecureRequestWarning）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HttpChecker:
    """HTTP检查器"""

    def __init__(self, timeout: int = 10, max_retries: int = 1, delay: float = 0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay
        self.session = requests.Session()

        # 配置会话
        self.session.headers.update({
            "User-Agent": "API_Aspects_Isolation_Checker/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        })
        # 禁用SSL证书验证，支持内部域名（自签名证书等）
        self.session.verify = False

    def check(self, domain: str, api: str, method: str = "GET",
              data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        start_time = time.time()

        try:
            url = self._build_url(domain, api)

            request_kwargs = {
                "timeout": self.timeout,
                "allow_redirects": True
            }

            if headers:
                request_headers = self.session.headers.copy()
                request_headers.update(headers)
                request_kwargs["headers"] = request_headers

            if data and method in ["POST", "PUT", "PATCH"]:
                request_kwargs["json"] = data

            response = None

            for attempt in range(self.max_retries + 1):
                try:
                    response = self.session.request(
                        method=method,
                        url=url,
                        **request_kwargs
                    )
                    break

                except requests.exceptions.Timeout:
                    if attempt < self.max_retries:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception("请求超时")

                except requests.exceptions.ConnectionError:
                    if attempt < self.max_retries:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception("无法连接到服务器")

                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception(f"请求失败: {str(e)}")

        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "status_code": None,
                "url": f"{domain}{api}" if domain and api else "N/A"
            }
        finally:
            if self.delay > 0:
                time.sleep(self.delay)

        response_time = int((time.time() - start_time) * 1000)

        result = {
            "success": True,
            "status_code": response.status_code,
            "response_time": response_time,
            "url": url,
            "headers": dict(response.headers),
            "error": None
        }

        return result

    def _build_url(self, domain: str, api: str) -> str:
        if not domain.startswith(("http://", "https://")):
            domain = f"http://{domain}"

        if api and not api.startswith("/"):
            api = f"/{api}"

        return urljoin(domain, api)
