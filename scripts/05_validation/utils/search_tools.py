#!/usr/bin/env python3
"""
外部验证工具模块 - LLM验证审核系统
External Verification Tools for LLM Validation Suite

提供各种外部验证和搜索功能
"""

import os
import re
import time
import urllib.parse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import requests
from datetime import datetime

import yaml


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    source: str
    query: str
    url: str
    timestamp: str
    results_found: bool = False
    title_match: bool = False
    author_match: bool = False
    confidence_score: float = 0.0
    notes: str = ""


class ExternalValidator:
    """外部验证工具类"""
    
    def __init__(self, config_path: str = "scripts/05_validation/validation_config.yaml"):
        # 如果是相对路径，从项目根目录开始查找
        if not os.path.isabs(config_path):
            # 尝试从当前目录、父目录、项目根目录查找
            possible_paths = [
                Path(config_path),
                Path("../") / config_path,
                Path("../../") / config_path,
                Path("../../../") / config_path
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break
        
        self.config = self._load_config(config_path)
        self.validation_config = self.config['external_validation']
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _clean_text_for_search(self, text: str) -> str:
        """清理文本用于搜索"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 截断过长的文本
        if len(text) > 100:
            text = text[:100] + "..."
        
        return text
    
    def _extract_first_author(self, authors_string: str) -> str:
        """提取第一作者姓名"""
        if not authors_string:
            return ""
        
        # 按分号分割，取第一个
        first_author = authors_string.split(';')[0].strip()
        
        # 移除机构信息等噪声
        if '(' in first_author:
            first_author = first_author.split('(')[0].strip()
        if '[' in first_author:
            first_author = first_author.split('[')[0].strip()
        
        return first_author
    
    def generate_search_urls(self, title: str, authors: str) -> List[Dict[str, str]]:
        """
        生成各种搜索URL
        返回: [{"name": "搜索引擎名称", "url": "搜索URL"}]
        """
        clean_title = self._clean_text_for_search(title)
        first_author = self._extract_first_author(authors)
        
        search_urls = []
        
        # Google Scholar
        if self.validation_config['google_scholar']['enabled']:
            base_url = self.validation_config['google_scholar']['base_url']
            query = f'"{clean_title}" "{first_author}"' if first_author else f'"{clean_title}"'
            encoded_query = urllib.parse.quote(query)
            url = f"{base_url}?q={encoded_query}"
            search_urls.append({"name": "Google Scholar", "url": url})
        
        # 自定义搜索模板
        if self.validation_config['custom_search']['enabled']:
            for template in self.validation_config['custom_search']['templates']:
                try:
                    url = template['url'].format(
                        title=urllib.parse.quote(clean_title),
                        author=urllib.parse.quote(first_author) if first_author else ""
                    )
                    search_urls.append({"name": template['name'], "url": url})
                except KeyError:
                    continue
        
        return search_urls
    
    def crossref_search(self, title: str, authors: str) -> SearchResult:
        """
        使用CrossRef API搜索
        """
        if not self.validation_config['crossref']['enabled']:
            return SearchResult(
                source="CrossRef",
                query=f"{title} {authors}",
                url="",
                timestamp=datetime.now().isoformat(),
                notes="CrossRef搜索已禁用"
            )
        
        clean_title = self._clean_text_for_search(title)
        first_author = self._extract_first_author(authors)
        
        api_url = self.validation_config['crossref']['api_url']
        query = f"{clean_title} {first_author}".strip()
        
        params = {
            'query': query,
            'rows': 5,
            'select': 'title,author,DOI,URL'
        }
        
        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            result = SearchResult(
                source="CrossRef",
                query=query,
                url=response.url,
                timestamp=datetime.now().isoformat(),
                results_found=len(items) > 0
            )
            
            # 简单的匹配检查
            if items:
                first_item = items[0]
                item_title = first_item.get('title', [''])[0] if first_item.get('title') else ''
                
                # 标题相似度检查（简单的词重叠）
                title_words = set(clean_title.lower().split())
                item_title_words = set(item_title.lower().split())
                
                if title_words and item_title_words:
                    overlap = len(title_words.intersection(item_title_words))
                    result.confidence_score = overlap / len(title_words.union(item_title_words))
                    result.title_match = result.confidence_score > 0.3
                
                result.notes = f"找到 {len(items)} 个结果，最佳匹配: {item_title[:50]}..."
            else:
                result.notes = "未找到匹配结果"
            
            return result
            
        except Exception as e:
            return SearchResult(
                source="CrossRef",
                query=query,
                url="",
                timestamp=datetime.now().isoformat(),
                notes=f"搜索失败: {str(e)}"
            )
    
    def orcid_search(self, authors: str) -> SearchResult:
        """
        使用ORCID API搜索作者
        """
        if not self.validation_config['orcid']['enabled']:
            return SearchResult(
                source="ORCID",
                query=authors,
                url="",
                timestamp=datetime.now().isoformat(),
                notes="ORCID搜索已禁用"
            )
        
        first_author = self._extract_first_author(authors)
        if not first_author:
            return SearchResult(
                source="ORCID",
                query="",
                url="",
                timestamp=datetime.now().isoformat(),
                notes="无有效作者姓名"
            )
        
        api_url = self.validation_config['orcid']['api_url']
        
        params = {
            'q': f'given-names:{first_author} OR family-name:{first_author}',
            'rows': 5
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        try:
            response = self.session.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('result', [])
            
            result = SearchResult(
                source="ORCID",
                query=first_author,
                url=response.url,
                timestamp=datetime.now().isoformat(),
                results_found=len(results) > 0,
                author_match=len(results) > 0
            )
            
            if results:
                result.confidence_score = min(1.0, len(results) / 5.0)
                result.notes = f"找到 {len(results)} 个可能的ORCID记录"
            else:
                result.notes = "未找到ORCID记录"
            
            return result
            
        except Exception as e:
            return SearchResult(
                source="ORCID",
                query=first_author,
                url="",
                timestamp=datetime.now().isoformat(),
                notes=f"搜索失败: {str(e)}"
            )
    
    def comprehensive_validation(self, title: str, authors: str) -> Dict[str, Any]:
        """
        综合验证：使用多个源进行验证
        """
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'authors': authors,
            'search_urls': self.generate_search_urls(title, authors),
            'api_results': {}
        }
        
        # CrossRef搜索
        crossref_result = self.crossref_search(title, authors)
        validation_results['api_results']['crossref'] = crossref_result
        
        # 添加延迟避免API限制
        time.sleep(1)
        
        # ORCID搜索
        orcid_result = self.orcid_search(authors)
        validation_results['api_results']['orcid'] = orcid_result
        
        # 计算综合置信度
        confidence_scores = []
        if crossref_result.confidence_score > 0:
            confidence_scores.append(crossref_result.confidence_score)
        if orcid_result.confidence_score > 0:
            confidence_scores.append(orcid_result.confidence_score * 0.7)  # ORCID权重较低
        
        validation_results['overall_confidence'] = (
            sum(confidence_scores) / len(confidence_scores) 
            if confidence_scores else 0.0
        )
        
        # 生成验证建议
        if validation_results['overall_confidence'] > 0.7:
            validation_results['recommendation'] = "高置信度：很可能正确"
        elif validation_results['overall_confidence'] > 0.4:
            validation_results['recommendation'] = "中等置信度：需要人工确认"
        else:
            validation_results['recommendation'] = "低置信度：可能存在问题"
        
        return validation_results


class SearchURLGenerator:
    """搜索URL生成器（静态方法集合）"""
    
    @staticmethod
    def google_scholar_url(title: str, author: str = "") -> str:
        """生成Google Scholar搜索URL"""
        query = f'"{title}"'
        if author:
            query += f' "{author}"'
        encoded_query = urllib.parse.quote(query)
        return f"https://scholar.google.com/scholar?q={encoded_query}"
    
    @staticmethod
    def semantic_scholar_url(title: str, author: str = "") -> str:
        """生成Semantic Scholar搜索URL"""
        query = f'"{title}"'
        if author:
            query += f' "{author}"'
        encoded_query = urllib.parse.quote(query)
        return f"https://www.semanticscholar.org/search?q={encoded_query}"
    
    @staticmethod
    def pubmed_url(title: str, author: str = "") -> str:
        """生成PubMed搜索URL"""
        query = f'"{title}"[Title]'
        if author:
            query += f' AND "{author}"[Author]'
        encoded_query = urllib.parse.quote(query)
        return f"https://pubmed.ncbi.nlm.nih.gov/?term={encoded_query}"
    
    @staticmethod
    def ieee_url(title: str, author: str = "") -> str:
        """生成IEEE Xplore搜索URL"""
        query = f'"{title}"'
        if author:
            query += f' "{author}"'
        encoded_query = urllib.parse.quote(query)
        return f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={encoded_query}"


def main():
    """测试外部验证工具"""
    validator = ExternalValidator()
    
    # 测试数据
    test_title = "Machine Learning Applications in Healthcare"
    test_authors = "Smith, John; Johnson, Mary"
    
    print("🔍 测试外部验证工具...")
    
    print("\n📎 生成搜索URL:")
    search_urls = validator.generate_search_urls(test_title, test_authors)
    for url_info in search_urls:
        print(f"  {url_info['name']}: {url_info['url']}")
    
    print("\n🔍 CrossRef搜索测试:")
    crossref_result = validator.crossref_search(test_title, test_authors)
    print(f"  结果: {crossref_result.notes}")
    print(f"  置信度: {crossref_result.confidence_score:.2f}")
    
    print("\n🆔 ORCID搜索测试:")
    orcid_result = validator.orcid_search(test_authors)
    print(f"  结果: {orcid_result.notes}")
    print(f"  置信度: {orcid_result.confidence_score:.2f}")
    
    print("\n🎯 综合验证测试:")
    comprehensive_result = validator.comprehensive_validation(test_title, test_authors)
    print(f"  综合置信度: {comprehensive_result['overall_confidence']:.2f}")
    print(f"  建议: {comprehensive_result['recommendation']}")


if __name__ == "__main__":
    main()
