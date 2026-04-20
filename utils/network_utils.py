"""
网络工具类
"""

import socket
import requests
import urllib.parse
from typing import Optional, Tuple, Dict, Any
import ipaddress


class NetworkUtils:
    """网络工具类"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: URL字符串
            
        Returns:
            是否有效
        """
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        标准化URL
        
        Args:
            url: 原始URL
            
        Returns:
            标准化后的URL
        """
        if not url:
            return ""
            
        # 确保有协议前缀
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
            
        # 解析URL
        parsed = urllib.parse.urlparse(url)
        
        # 重建URL（标准化）
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),  # 域名转小写
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        return normalized
        
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        从URL中提取域名
        
        Args:
            url: URL字符串
            
        Returns:
            域名，如果无效则返回None
        """
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc
        except:
            return None
            
    @staticmethod
    def is_ip_address(host: str) -> bool:
        """
        检查是否为IP地址
        
        Args:
            host: 主机名或IP地址
            
        Returns:
            是否为IP地址
        """
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False
            
    @staticmethod
    def resolve_hostname(hostname: str) -> Optional[str]:
        """
        解析主机名到IP地址
        
        Args:
            hostname: 主机名
            
        Returns:
            IP地址，如果无法解析则返回None
        """
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None
            
    @staticmethod
    def check_connectivity(url: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """
        检查网络连接性
        
        Args:
            url: 测试URL
            timeout: 超时时间（秒）
            
        Returns:
            (是否可连接, 错误信息)
        """
        try:
            # 尝试HEAD请求（更轻量）
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return True, None
        except requests.exceptions.Timeout:
            return False, "连接超时"
        except requests.exceptions.ConnectionError:
            return False, "无法连接"
        except requests.exceptions.RequestException as e:
            return False, f"连接错误: {str(e)}"
            
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """
        获取网络信息
        
        Returns:
            网络信息字典
        """
        try:
            import socket
            
            info = {
                "hostname": socket.gethostname(),
                "local_ip": socket.gethostbyname(socket.gethostname()),
                "public_ip": NetworkUtils.get_public_ip(),
                "is_connected": False
            }
            
            # 检查互联网连接
            connected, error = NetworkUtils.check_connectivity("http://www.baidu.com", 3)
            info["is_connected"] = connected
            info["connection_error"] = error if not connected else None
            
            return info
            
        except Exception as e:
            return {
                "error": str(e),
                "is_connected": False
            }
            
    @staticmethod
    def get_public_ip() -> Optional[str]:
        """
        获取公网IP地址
        
        Returns:
            公网IP地址，如果无法获取则返回None
        """
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            if response.status_code == 200:
                return response.json().get("ip")
        except:
            pass
            
        # 备用API
        try:
            response = requests.get("https://httpbin.org/ip", timeout=5)
            if response.status_code == 200:
                return response.json().get("origin")
        except:
            pass
            
        return None
        
    @staticmethod
    def validate_port(port: int) -> bool:
        """
        验证端口号
        
        Args:
            port: 端口号
            
        Returns:
            是否有效
        """
        return 1 <= port <= 65535
        
    @staticmethod
    def is_port_open(host: str, port: int, timeout: int = 2) -> bool:
        """
        检查端口是否开放
        
        Args:
            host: 主机名或IP地址
            port: 端口号
            timeout: 超时时间（秒）
            
        Returns:
            端口是否开放
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
            
    @staticmethod
    def build_url(domain: str, path: str, use_https: bool = False) -> str:
        """
        构建完整URL
        
        Args:
            domain: 域名
            path: 路径
            use_https: 是否使用HTTPS
            
        Returns:
            完整URL
        """
        # 清理域名
        domain = domain.strip()
        if domain.startswith(("http://", "https://")):
            domain = NetworkUtils.extract_domain(domain) or domain
            
        # 清理路径
        path = path.strip()
        if path and not path.startswith("/"):
            path = f"/{path}"
            
        # 构建URL
        protocol = "https" if use_https else "http"
        return f"{protocol}://{domain}{path}"
        
    @staticmethod
    def parse_http_method(method: str) -> str:
        """
        解析HTTP方法
        
        Args:
            method: HTTP方法字符串
            
        Returns:
            标准化的HTTP方法
        """
        method = method.strip().upper()
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        if method in valid_methods:
            return method
        else:
            return "GET"  # 默认使用GET