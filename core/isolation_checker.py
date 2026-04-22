"""
隔离检查器
"""

from typing import Optional


class IsolationChecker:
    """隔离检查器"""

    def __init__(self):
        self.isolation_codes = {
            "运行集成面": 403,
            "运维管理面": 403,
            "用户访问面": 403
        }

    def check(self, aspect: str, status_code: Optional[int],
              response_time: Optional[float] = None) -> str:
        if not aspect:
            return "错误: 切面分类为空"

        if status_code is None:
            return "错误: 无法获取状态码"

        aspect = aspect.strip()

        if aspect not in self.isolation_codes:
            return f"警告: 不支持的切面分类 '{aspect}'"

        required_code = self.isolation_codes[aspect]

        if aspect == "用户访问面":
            result = f"用户访问面，状态码：{status_code}"
        elif status_code == 404:
            result = "非本应用API，请确认"
        elif status_code == required_code:
            result = f"{aspect}API已隔离"
        else:
            result = f"{aspect}API未隔离"

        return result
