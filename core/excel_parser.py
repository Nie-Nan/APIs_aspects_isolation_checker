"""
Excel文件解析器
"""

import pandas as pd
from typing import List, Dict, Any


class ExcelParser:
    """Excel文件解析器"""

    REQUIRED_COLUMNS = ["切面分类", "域名", "API", "请求方式"]

    def __init__(self):
        self.data = []

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            df = pd.read_excel(file_path)

            missing_columns = []
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    missing_columns.append(col)

            if missing_columns:
                raise ValueError(f"Excel文件中缺少必需字段: {', '.join(missing_columns)}")

            self.data = []
            for _, row in df.iterrows():
                records = self._process_record(row)
                if records:
                    if isinstance(records, list):
                        self.data.extend(records)
                    else:
                        self.data.append(records)

            return self.data

        except Exception as e:
            raise Exception(f"解析Excel文件失败: {str(e)}")

    def _process_record(self, row: pd.Series) -> List[Dict[str, Any]]:
        try:
            aspect = str(row["切面分类"]).strip()

            domain_str = str(row["域名"]).strip()
            domains = self._parse_domains(domain_str)

            api = str(row["API"]).strip()

            method = str(row["请求方式"]).strip().upper()

            if not aspect:
                raise ValueError("切面分类不能为空")
            if not domains:
                raise ValueError("域名不能为空")
            if not api:
                raise ValueError("API不能为空")
            if not method:
                method = "GET"

            records = []
            for domain in domains:
                record = {
                    "切面分类": aspect,
                    "域名": domain,
                    "API": api,
                    "请求方式": method,
                    "原始域名": domain_str
                }
                records.append(record)

            return records

        except Exception as e:
            print(f"处理记录时出错: {str(e)}")
            return []

    def _parse_domains(self, domain_str: str) -> List[str]:
        if not domain_str:
            return []

        separators = [',', ';', '\n', '\t', '|', '、']

        normalized = domain_str
        for sep in separators:
            normalized = normalized.replace(sep, ',')

        domains = []
        for domain in normalized.split(','):
            domain = domain.strip()
            if domain:
                domain = self._clean_domain(domain)
                domains.append(domain)

        return domains

    def _clean_domain(self, domain: str) -> str:
        domain = domain.strip()

        if "://" in domain:
            from urllib.parse import urlparse
            parsed = urlparse(domain)
            domain = parsed.netloc
            if parsed.scheme:
                domain = f"{parsed.scheme}://{domain}"

        return domain
