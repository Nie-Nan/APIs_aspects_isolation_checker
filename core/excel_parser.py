"""
Excel文件解析器
"""

import pandas as pd
import re
from typing import List, Dict, Any


class ExcelParser:
    """Excel文件解析器"""
    
    REQUIRED_COLUMNS = ["切面分类", "域名", "API", "请求方式"]
    
    def __init__(self):
        self.data = []
        
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            解析后的数据列表
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 验证必需字段
            missing_columns = []
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    missing_columns.append(col)
                    
            if missing_columns:
                raise ValueError(f"Excel文件中缺少必需字段: {', '.join(missing_columns)}")
                
            # 处理数据
            self.data = []
            for _, row in df.iterrows():
                records = self._process_record(row)
                if records:
                    # 如果返回的是列表，则展平
                    if isinstance(records, list):
                        self.data.extend(records)
                    else:
                        self.data.append(records)
                    
            return self.data
            
        except Exception as e:
            raise Exception(f"解析Excel文件失败: {str(e)}")
            
    def _process_record(self, row: pd.Series) -> List[Dict[str, Any]]:
        """
        处理单条记录
        
        Args:
            row: DataFrame行数据
            
        Returns:
            处理后的记录字典列表（一个域名对应一个字典）
        """
        try:
            # 获取切面分类
            aspect = str(row["切面分类"]).strip()
            
            # 处理域名（支持多域名）
            domain_str = str(row["域名"]).strip()
            domains = self._parse_domains(domain_str)
            
            # 获取API
            api = str(row["API"]).strip()
            
            # 获取请求方式
            method = str(row["请求方式"]).strip().upper()
            
            # 验证数据
            if not aspect:
                raise ValueError("切面分类不能为空")
            if not domains:
                raise ValueError("域名不能为空")
            if not api:
                raise ValueError("API不能为空")
            if not method:
                method = "GET"
                
            # 为每个域名创建一条记录
            records = []
            for domain in domains:
                record = {
                    "切面分类": aspect,
                    "域名": domain,
                    "API": api,
                    "请求方式": method,
                    "原始域名": domain_str  # 保留原始域名字符串
                }
                records.append(record)
                
            return records
            
        except Exception as e:
            print(f"处理记录时出错: {str(e)}")
            return []
            
    def _parse_domains(self, domain_str: str) -> List[str]:
        """
        解析域名字符串，支持多种分隔符
        
        Args:
            domain_str: 域名字符串
            
        Returns:
            域名列表
        """
        if not domain_str:
            return []
            
        # 常见分隔符：逗号、分号、空格、换行、制表符
        separators = [',', ';', '\n', '\t', '|', '、']
        
        # 替换所有分隔符为逗号
        normalized = domain_str
        for sep in separators:
            normalized = normalized.replace(sep, ',')
            
        # 分割并清理
        domains = []
        for domain in normalized.split(','):
            domain = domain.strip()
            if domain:
                # 清理域名
                domain = self._clean_domain(domain)
                domains.append(domain)
                
        return domains
        
    def _clean_domain(self, domain: str) -> str:
        """
        清理域名
        
        Args:
            domain: 原始域名
            
        Returns:
            清理后的域名
        """
        domain = domain.strip()
        
        # 如果包含协议，提取 scheme://netloc；否则直接保留原样（支持 host:port）
        if "://" in domain:
            from urllib.parse import urlparse
            parsed = urlparse(domain)
            domain = parsed.netloc
            if parsed.scheme:
                domain = f"{parsed.scheme}://{domain}"
                
        return domain
        
    def validate_domain(self, domain: str) -> bool:
        """
        验证域名格式
        
        Args:
            domain: 域名
            
        Returns:
            是否有效
        """
        # 简单的域名验证
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain))
        
    def get_summary(self) -> Dict[str, Any]:
        """
        获取数据摘要
        
        Returns:
            数据摘要字典
        """
        if not self.data:
            return {}
            
        # 统计切面分类
        aspect_counts = {}
        for record in self.data:
            aspect = record["切面分类"]
            aspect_counts[aspect] = aspect_counts.get(aspect, 0) + 1
            
        # 统计域名数量
        unique_domains = set()
        for record in self.data:
            unique_domains.add(record["域名"])
            
        # 统计请求方式
        method_counts = {}
        for record in self.data:
            method = record["请求方式"]
            method_counts[method] = method_counts.get(method, 0) + 1
            
        return {
            "total_records": len(self.data),
            "aspect_counts": aspect_counts,
            "unique_domains": len(unique_domains),
            "method_counts": method_counts
        }