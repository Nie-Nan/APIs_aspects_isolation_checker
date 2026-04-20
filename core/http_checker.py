"""
HTTP检查器
"""

import requests
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class HttpChecker:
    """HTTP检查器"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 1, delay: float = 0):
        """
        初始化HTTP检查器
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            delay: 每次请求后的间隔时间（秒），用于降低请求频率避免触发流控
        """
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
        
    def check(self, domain: str, api: str, method: str = "GET", 
              data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        检查API
        
        Args:
            domain: 域名
            api: API路径
            method: 请求方式
            data: 请求数据（用于POST/PUT等）
            headers: 自定义请求头
            
        Returns:
            检查结果字典
        """
        start_time = time.time()
        
        try:
            # 构建完整URL
            url = self._build_url(domain, api)
            
            # 准备请求参数
            request_kwargs = {
                "timeout": self.timeout,
                "allow_redirects": True  # 自动跟随重定向，获取最终状态码
            }
            
            # 添加自定义请求头
            if headers:
                request_headers = self.session.headers.copy()
                request_headers.update(headers)
                request_kwargs["headers"] = request_headers
                
            # 添加请求数据
            if data and method in ["POST", "PUT", "PATCH"]:
                request_kwargs["json"] = data
                
            # 发送请求（支持重试）
            response = None
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.session.request(
                        method=method,
                        url=url,
                        **request_kwargs
                    )
                    break  # 请求成功，跳出重试循环
                    
                except requests.exceptions.Timeout:
                    last_exception = "请求超时"
                    if attempt < self.max_retries:
                        time.sleep(1)  # 重试前等待1秒
                        continue
                    else:
                        raise Exception("请求超时")
                        
                except requests.exceptions.ConnectionError:
                    last_exception = "连接错误"
                    if attempt < self.max_retries:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception("无法连接到服务器")
                        
                except requests.exceptions.RequestException as e:
                    last_exception = str(e)
                    if attempt < self.max_retries:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception(f"请求失败: {str(e)}")
                        
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)  # 转换为毫秒
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "status_code": None,
                "url": f"{domain}{api}" if domain and api else "N/A"
            }
        finally:
            # 请求间隔，降低频率避免触发服务端流控
            if self.delay > 0:
                time.sleep(self.delay)
            
        # 计算响应时间
        response_time = int((time.time() - start_time) * 1000)  # 转换为毫秒
        
        # 构建结果
        result = {
            "success": True,
            "status_code": response.status_code,
            "response_time": response_time,
            "url": url,
            "headers": dict(response.headers),
            "error": None
        }
        
        # 尝试获取响应内容（如果有）
        try:
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                result["response_data"] = response.json()
            elif "text/" in content_type:
                result["response_text"] = response.text[:500]  # 只取前500字符
        except:
            pass  # 忽略解析错误
            
        return result
        
    def _build_url(self, domain: str, api: str) -> str:
        """
        构建完整URL
        
        Args:
            domain: 域名
            api: API路径
            
        Returns:
            完整URL
        """
        # 确保域名有协议前缀
        if not domain.startswith(("http://", "https://")):
            domain = f"http://{domain}"  # 默认使用HTTP
            
        # 确保API路径以/开头
        if api and not api.startswith("/"):
            api = f"/{api}"
            
        # 拼接URL
        return urljoin(domain, api)
        
    def validate_url(self, url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: URL字符串
            
        Returns:
            是否有效
        """
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def test_connection(self, url: str) -> Dict[str, Any]:
        """
        测试连接
        
        Args:
            url: 测试URL
            
        Returns:
            测试结果
        """
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "连接正常"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": None,
                "message": "连接超时"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": None,
                "message": "无法连接"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"连接错误: {str(e)}"
            }
            
    def set_proxy(self, proxy: Optional[Dict[str, str]] = None):
        """
        设置代理
        
        Args:
            proxy: 代理配置，例如 {"http": "http://proxy:port", "https": "https://proxy:port"}
        """
        if proxy:
            self.session.proxies.update(proxy)
        else:
            self.session.proxies.clear()
            
    def close(self):
        """关闭会话"""
        self.session.close()