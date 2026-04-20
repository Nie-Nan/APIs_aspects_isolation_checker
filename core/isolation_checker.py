"""
隔离检查器
"""

from typing import Optional


class IsolationChecker:
    """隔离检查器"""
    
    def __init__(self):
        """初始化隔离检查器"""
        self.isolation_codes = {
            "运行集成面": 403,
            "运维管理面": 403,
            "用户访问面": 403
        }
        
    def check(self, aspect: str, status_code: Optional[int], 
              response_time: Optional[float] = None) -> str:
        """
        检查隔离状态
        
        Args:
            aspect: 切面分类
            status_code: HTTP状态码
            response_time: 响应时间（毫秒）
            
        Returns:
            检查结果字符串
        """
        # 验证输入
        if not aspect:
            return "错误: 切面分类为空"
            
        if status_code is None:
            return "错误: 无法获取状态码"
            
        # 标准化切面分类
        aspect = aspect.strip()
        
        # 检查是否支持该切面
        if aspect not in self.isolation_codes:
            return f"警告: 不支持的切面分类 '{aspect}'"
            
        # 获取该切面要求的隔离状态码
        required_code = self.isolation_codes[aspect]
        
        # 判断隔离状态
        if aspect == "用户访问面":
            result = f"用户访问面，状态码：{status_code}"
        elif status_code == 404:
            result = "非本应用API，请确认"
        elif status_code == required_code:
            result = f"{aspect}API已隔离"
        else:
            result = f"{aspect}API未隔离"
            
        return result
        
    def get_isolation_rule(self, aspect: str) -> Optional[int]:
        """
        获取切面的隔离规则
        
        Args:
            aspect: 切面分类
            
        Returns:
            要求的HTTP状态码，如果不支持则返回None
        """
        return self.isolation_codes.get(aspect)
        
    def add_isolation_rule(self, aspect: str, status_code: int) -> bool:
        """
        添加隔离规则
        
        Args:
            aspect: 切面分类
            status_code: 要求的HTTP状态码
            
        Returns:
            是否添加成功
        """
        if not aspect or not isinstance(status_code, int):
            return False
            
        self.isolation_codes[aspect] = status_code
        return True
        
    def remove_isolation_rule(self, aspect: str) -> bool:
        """
        移除隔离规则
        
        Args:
            aspect: 切面分类
            
        Returns:
            是否移除成功
        """
        if aspect in self.isolation_codes:
            del self.isolation_codes[aspect]
            return True
        return False
        
    def get_all_rules(self) -> dict:
        """
        获取所有隔离规则
        
        Returns:
            隔离规则字典
        """
        return self.isolation_codes.copy()
        
    def validate_aspect(self, aspect: str) -> bool:
        """
        验证切面分类是否支持
        
        Args:
            aspect: 切面分类
            
        Returns:
            是否支持
        """
        return aspect in self.isolation_codes
        
    def get_check_summary(self, results: list) -> dict:
        """
        获取检查结果摘要
        
        Args:
            results: 检查结果列表，每个元素为字典，包含aspect和result
            
        Returns:
            摘要字典
        """
        summary = {
            "total": len(results),
            "isolated": 0,
            "not_isolated": 0,
            "errors": 0,
            "by_aspect": {}
        }
        
        for result in results:
            aspect = result.get("aspect", "未知")
            result_str = result.get("result", "")
            
            # 初始化该切面的统计
            if aspect not in summary["by_aspect"]:
                summary["by_aspect"][aspect] = {
                    "total": 0,
                    "isolated": 0,
                    "not_isolated": 0,
                    "errors": 0
                }
                
            # 更新统计
            summary["by_aspect"][aspect]["total"] += 1
            
            if "已隔离" in result_str:
                summary["isolated"] += 1
                summary["by_aspect"][aspect]["isolated"] += 1
            elif "未隔离" in result_str:
                summary["not_isolated"] += 1
                summary["by_aspect"][aspect]["not_isolated"] += 1
            else:
                summary["errors"] += 1
                summary["by_aspect"][aspect]["errors"] += 1
                
        return summary
        
    def format_result_for_display(self, aspect: str, status_code: int, 
                                  response_time: Optional[float] = None) -> dict:
        """
        格式化检查结果用于显示
        
        Args:
            aspect: 切面分类
            status_code: HTTP状态码
            response_time: 响应时间（毫秒）
            
        Returns:
            格式化后的结果字典
        """
        result_str = self.check(aspect, status_code, response_time)
        
        formatted = {
            "aspect": aspect,
            "status_code": status_code,
            "response_time": response_time,
            "result": result_str,
            "is_isolated": "已隔离" in result_str,
            "has_error": "错误" in result_str or "警告" in result_str
        }
        
        return formatted