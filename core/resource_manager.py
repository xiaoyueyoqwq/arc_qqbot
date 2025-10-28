# -*- coding: utf-8 -*-
"""
资源管理器 - 加载和管理游戏资源索引
"""
import orjson as json
from pathlib import Path
from typing import Dict, Optional, List, Any
from utils.logger import bot_logger


class ResourceManager:
    """资源管理器类"""
    
    def __init__(self, resource_dir: str = "resources"):
        """
        初始化资源管理器
        
        Args:
            resource_dir: 资源根目录
        """
        self.resource_dir = Path(resource_dir)
        self.resource_files = {
            "maps": self.resource_dir / "maps.json",
            "weapons": self.resource_dir / "weapons.json",
            "arc": self.resource_dir / "arc.json"
        }
        self.resources: Dict[str, Dict] = {
            "maps": {},
            "weapons": {},
            "arc": {}
        }
        self.load_resources()
    
    def load_resources(self) -> bool:
        """
        加载所有资源索引文件
        
        Returns:
            bool: 加载是否成功
        """
        success = True
        
        for category, file_path in self.resource_files.items():
            try:
                if not file_path.exists():
                    bot_logger.warning(f"资源文件不存在: {file_path}")
                    continue
                
                with open(file_path, 'rb') as f:
                    self.resources[category] = json.loads(f.read())
                
                count = len(self.resources[category])
                bot_logger.info(f"加载 {category} 资源: {count} 个")
                
            except Exception as e:
                bot_logger.error(f"加载 {category} 资源失败: {e}", exc_info=True)
                success = False
        
        total = sum(len(r) for r in self.resources.values())
        bot_logger.info(f"资源加载完成，共 {total} 个资源")
        return success
    
    def reload_resources(self) -> bool:
        """
        重新加载资源索引
        
        Returns:
            bool: 加载是否成功
        """
        return self.load_resources()
    
    def find_resource(
        self, 
        category: str, 
        query: str
    ) -> Optional[Dict[str, Any]]:
        """
        查找资源
        
        Args:
            category: 资源类别 (maps/weapons/arc)
            query: 查询关键词
            
        Returns:
            Dict: 资源信息，未找到返回None
        """
        if category not in self.resources:
            return None
        
        query_lower = query.lower().strip()
        
        # 遍历该类别下的所有资源
        for key, resource in self.resources[category].items():
            # 精确匹配资源名称
            if key.lower() == query_lower or resource.get('name', '').lower() == query_lower:
                return self._build_resource_info(category, key, resource)
            
            # 匹配别名
            aliases = resource.get('aliases', [])
            if any(alias.lower() == query_lower for alias in aliases):
                return self._build_resource_info(category, key, resource)
        
        # 模糊匹配
        for key, resource in self.resources[category].items():
            if query_lower in key.lower() or query_lower in resource.get('name', '').lower():
                return self._build_resource_info(category, key, resource)
            
            aliases = resource.get('aliases', [])
            if any(query_lower in alias.lower() for alias in aliases):
                return self._build_resource_info(category, key, resource)
        
        return None
    
    def _build_resource_info(
        self, 
        category: str, 
        key: str, 
        resource: Dict
    ) -> Dict[str, Any]:
        """
        构建资源信息
        
        Args:
            category: 资源类别
            key: 资源键
            resource: 资源数据
            
        Returns:
            Dict: 完整的资源信息
        """
        # 构建文件路径
        filename = resource.get('filename')
        if filename:
            file_path = self.resource_dir / category / filename
        else:
            file_path = None
        
        return {
            'key': key,
            'category': category,
            'name': resource.get('name', key),
            'filename': filename,
            'file_path': str(file_path) if file_path else None,
            'description': resource.get('description', ''),
            'type': resource.get('type', ''),
            'aliases': resource.get('aliases', []),
            'exists': file_path.exists() if file_path else False
        }
    
    def list_resources(self, category: str) -> List[Dict[str, Any]]:
        """
        列出指定类别的所有资源
        
        Args:
            category: 资源类别 (maps/weapons/arc)
            
        Returns:
            List[Dict]: 资源列表
        """
        if category not in self.resources:
            return []
        
        result = []
        for key, resource in self.resources[category].items():
            result.append(self._build_resource_info(category, key, resource))
        
        return result
    
    def get_all_names(self, category: str) -> List[str]:
        """
        获取指定类别的所有资源名称
        
        Args:
            category: 资源类别
            
        Returns:
            List[str]: 资源名称列表
        """
        if category not in self.resources:
            return []
        
        return [resource.get('name', key) for key, resource in self.resources[category].items()]
    
    def find_weapon_with_level(
        self, 
        query: str, 
        level: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        查找武器资源（支持等级查询）
        
        Args:
            query: 查询关键词
            level: 武器等级（可选）
            
        Returns:
            Dict: 武器信息，包含 has_levels、levels_available、weapon_data 等字段
        """
        # 先查找武器基础信息
        weapon = self.find_resource('weapons', query)
        if not weapon:
            return None
        
        # 从原始数据中获取完整信息
        weapon_key = weapon['key']
        weapon_data = self.resources['weapons'].get(weapon_key, {})
        
        # 检查是否有等级信息
        levels_data = weapon_data.get('levels', {})
        
        if not levels_data:
            # 没有等级信息，返回基础信息
            return {
                'has_levels': False,
                'weapon_data': weapon,
                'levels_available': []
            }
        
        # 有等级信息
        levels_available = sorted([int(lv) for lv in levels_data.keys()])
        
        if level is None:
            # 没有指定等级，返回所有等级信息
            return {
                'has_levels': True,
                'weapon_data': weapon,
                'levels_available': levels_available,
                'need_level_selection': True
            }
        
        # 检查指定的等级是否存在
        if level not in levels_available:
            return {
                'has_levels': True,
                'weapon_data': weapon,
                'levels_available': levels_available,
                'invalid_level': level,
                'need_level_selection': True
            }
        
        # 返回指定等级的武器信息
        level_info = levels_data.get(str(level), {})
        file_path = self.resource_dir / 'weapons' / level_info.get('filename', '')
        
        return {
            'has_levels': True,
            'weapon_data': weapon,
            'levels_available': levels_available,
            'selected_level': level,
            'level_info': {
                'filename': level_info.get('filename'),
                'file_path': str(file_path) if file_path else None,
                'exists': file_path.exists() if file_path else False
            },
            'need_level_selection': False
        }


# 全局单例
_resource_manager_instance: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """
    获取资源管理器单例
    
    Returns:
        ResourceManager: 资源管理器实例
    """
    global _resource_manager_instance
    if _resource_manager_instance is None:
        _resource_manager_instance = ResourceManager()
    return _resource_manager_instance

