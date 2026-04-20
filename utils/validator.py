"""
数据验证器
"""

import re
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse


class Validator:
    """数据验证器"""
    
    @staticmethod
    def validate_aspect(aspect: str) -> Tuple[bool, Optional[str]]:
        """
        验证切面分类
        
        Args:
            aspect: 切面分类字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not aspect or not aspect.strip():
            return False, "切面分类不能为空"
            
        aspect = aspect.strip()
        
        # 检查是否包含非法字符
        if re.search(r'[<>:"/\\|?*]', aspect):
            return False, "切面分类包含非法字符"
            
        # 检查长度
        if len(aspect) > 50:
            return False, "切面分类过长（最大50字符）"
            
        return True, None
        
    @staticmethod
    def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
        """
        验证域名
        
        Args:
            domain: 域名字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not domain or not domain.strip():
            return False, "域名不能为空"
            
        domain = domain.strip()
        
        # 移除协议前缀
        domain = re.sub(r'^https?://', '', domain)
        
        # 移除路径部分
        domain = domain.split('/')[0]
        
        # 移除端口号
        domain = domain.split(':')[0]
        
        # 检查是否为空
        if not domain:
            return False, "域名格式错误"
            
        # 检查长度
        if len(domain) > 253:
            return False, "域名过长"
            
        # 检查域名格式
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, domain):
            return False, "域名格式不正确"
            
        # 检查标签长度
        labels = domain.split('.')
        for label in labels:
            if len(label) > 63:
                return False, f"域名标签 '{label}' 过长（最大63字符）"
            if label.startswith('-') or label.endswith('-'):
                return False, f"域名标签 '{label}' 不能以连字符开头或结尾"
                
        return True, None
        
    @staticmethod
    def validate_api_path(api_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证API路径
        
        Args:
            api_path: API路径字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not api_path or not api_path.strip():
            return False, "API路径不能为空"
            
        api_path = api_path.strip()
        
        # 检查是否以/开头
        if not api_path.startswith('/'):
            return False, "API路径必须以 '/' 开头"
            
        # 检查长度
        if len(api_path) > 500:
            return False, "API路径过长（最大500字符）"
            
        # 检查是否包含非法字符
        if re.search(r'[<>:"\\|?*]', api_path):
            return False, "API路径包含非法字符"
            
        # 检查连续斜杠
        if '//' in api_path:
            return False, "API路径不能包含连续斜杠"
            
        return True, None
        
    @staticmethod
    def validate_http_method(method: str) -> Tuple[bool, Optional[str]]:
        """
        验证HTTP方法
        
        Args:
            method: HTTP方法字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not method or not method.strip():
            return False, "请求方式不能为空"
            
        method = method.strip().upper()
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        if method not in valid_methods:
            return False, f"不支持的HTTP方法。支持的方法: {', '.join(valid_methods)}"
            
        return True, None
        
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        验证URL
        
        Args:
            url: URL字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not url or not url.strip():
            return False, "URL不能为空"
            
        url = url.strip()
        
        try:
            result = urlparse(url)
            
            # 检查协议
            if not result.scheme:
                return False, "URL缺少协议（如 http:// 或 https://）"
                
            if result.scheme not in ['http', 'https']:
                return False, "只支持 HTTP 和 HTTPS 协议"
                
            # 检查网络位置
            if not result.netloc:
                return False, "URL缺少域名或IP地址"
                
            # 检查长度
            if len(url) > 2000:
                return False, "URL过长"
                
            return True, None
            
        except Exception as e:
            return False, f"URL解析错误: {str(e)}"
            
    @staticmethod
    def validate_status_code(status_code: Any) -> Tuple[bool, Optional[str]]:
        """
        验证HTTP状态码
        
        Args:
            status_code: 状态码
            
        Returns:
            (是否有效, 错误信息)
        """
        if status_code is None:
            return False, "状态码不能为空"
            
        try:
            code = int(status_code)
            
            # 检查范围
            if code < 100 or code > 599:
                return False, f"状态码 {code} 不在有效范围（100-599）内"
                
            return True, None
            
        except (ValueError, TypeError):
            return False, "状态码必须是整数"
            
    @staticmethod
    def validate_excel_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证Excel数据
        
        Args:
            data: Excel数据字典
            
        Returns:
            (是否有效, 错误信息)
        """
        required_fields = ["切面分类", "域名", "API", "请求方式"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in data:
                return False, f"缺少必需字段: {field}"
                
            value = data[field]
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, f"字段 '{field}' 不能为空"
                
        # 验证各个字段
        validators = {
            "切面分类": Validator.validate_aspect,
            "域名": Validator.validate_domain,
            "API": Validator.validate_api_path,
            "请求方式": Validator.validate_http_method
        }
        
        for field, validator_func in validators.items():
            value = str(data[field]).strip()
            is_valid, error_msg = validator_func(value)
            if not is_valid:
                return False, f"字段 '{field}' 验证失败: {error_msg}"
                
        return True, None
        
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        清理输入文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
            
        # 转换为字符串
        text = str(text)
        
        # 移除首尾空白
        text = text.strip()
        
        # 截断长度
        if len(text) > max_length:
            text = text[:max_length]
            
        # 移除控制字符（保留换行和制表符）
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
        
    @staticmethod
    def validate_response_time(response_time: Any) -> Tuple[bool, Optional[str]]:
        """
        验证响应时间
        
        Args:
            response_time: 响应时间
            
        Returns:
            (是否有效, 错误信息)
        """
        if response_time is None:
            return True, None  # 响应时间可以为空
            
        try:
            time_val = float(response_time)
            
            # 检查范围
            if time_val < 0:
                return False, "响应时间不能为负数"
            if time_val > 300000:  # 5分钟
                return False, "响应时间过长（超过5分钟）"
                
            return True, None
            
        except (ValueError, TypeError):
            return False, "响应时间必须是数字"