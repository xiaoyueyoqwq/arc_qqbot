# -*- coding: utf-8 -*-
"""
ARC Raiders 武器查询插件

提供武器查询功能，用户可以通过名称或别名查询武器信息
"""
import sys
import os

# 确保正确的路径设置
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Optional, Dict, Any
from pathlib import Path
from core.plugin import Plugin, on_command
from core.resource_manager import get_resource_manager
from utils.message_handler import MessageHandler
from utils.logger import bot_logger


class ARCWeaponPlugin(Plugin):
    """
    ARC Raiders 武器查询插件
    
    命令：
    - /weapon <武器名称> - 查询武器信息并显示武器图片
    - /weapon list - 列出所有可用武器
    """
    
    def __init__(self):
        super().__init__()
        self.resource_manager = get_resource_manager()
    
    async def on_load(self):
        """插件加载时调用"""
        await super().on_load()
        bot_logger.info(f"[{self.name}] 武器查询插件已加载")
    
    @on_command("weapon", "查询武器信息")
    async def handle_weapon(self, handler: MessageHandler, content: str):
        """
        处理 /weapon 命令
        
        用法：
        /weapon <武器名称> [等级] - 查询指定武器
        /weapon list - 列出所有武器
        
        示例：
        /weapon 示例武器     - 查看武器所有等级
        /weapon 示例武器 2   - 查看武器2级详情
        """
        # 提取查询参数
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await self._send_usage(handler)
            return
        
        query = parts[1].strip()
        
        # 列表命令
        if query.lower() in ['list', '列表', '全部']:
            await self._send_weapon_list(handler)
            return
        
        # 尝试解析武器名称和等级
        # 格式: "武器名称 等级" 或 "武器名称"
        query_parts = query.rsplit(maxsplit=1)
        weapon_name = query_parts[0] if len(query_parts) > 1 else query
        level = None
        
        # 检查最后一部分是否是数字（等级）
        if len(query_parts) > 1:
            try:
                level = int(query_parts[-1])
                weapon_name = ' '.join(query_parts[:-1])
            except ValueError:
                # 不是数字，整个都是武器名称
                weapon_name = query
                level = None
        
        # 查询武器
        await self._query_weapon(handler, weapon_name, level)
    
    async def _query_weapon(self, handler: MessageHandler, query: str, level: Optional[int] = None):
        """
        查询并发送武器信息
        
        Args:
            handler: 消息处理器
            query: 武器名称
            level: 武器等级（可选，默认为1）
        """
        try:
            # 如果没有指定等级，默认查询1级
            if level is None:
                level = 1
            
            # 使用等级查询方法
            result = self.resource_manager.find_weapon_with_level(query, level)
            
            if not result:
                await handler.send_text(
                    f"❌ 未找到武器: {query}\n"
                    f"💡 使用 /weapon list 查看所有可用武器"
                )
                return
            
            weapon_data = result['weapon_data']
            
            # 情况1: 没有等级的武器（简单武器）
            if not result['has_levels']:
                await self._send_simple_weapon(handler, weapon_data)
                return
            
            # 情况2: 有等级的武器
            # 如果指定的等级不存在，默认使用1级
            if result.get('need_level_selection', False):
                # 等级不存在，使用1级
                result = self.resource_manager.find_weapon_with_level(query, 1)
                if not result or result.get('need_level_selection', False):
                    await handler.send_text(f"❌ 武器数据错误: {query}")
                    return
            
            # 发送武器图片（不显示等级信息）
            await self._send_weapon_with_level(handler, weapon_data, result)
            
        except Exception as e:
            bot_logger.error(f"查询武器失败: {e}", exc_info=True)
            await handler.send_text("❌ 查询失败，请稍后重试")
    
    
    async def _send_simple_weapon(self, handler: MessageHandler, weapon_data: Dict):
        """发送简单武器信息（无等级）"""
        # 检查文件是否存在
        if not weapon_data['exists']:
            await handler.send_text(
                f"❌ 武器图片文件不存在\n"
                f"📁 文件路径: {weapon_data['file_path']}"
            )
            return
        
        # 使用新方法发送图片
        bot_logger.info(f"正在发送武器图片: {weapon_data['name']}")
        success = await handler.send_image_from_path(weapon_data['file_path'])
        
        if success:
            bot_logger.info(f"武器查询成功: {weapon_data['name']}")
        else:
            await handler.send_text(f"❌ 图片发送失败: {weapon_data['name']}")
    
    async def _send_weapon_with_level(
        self, 
        handler: MessageHandler, 
        weapon_data: Dict, 
        result: Dict
    ):
        """发送武器图片（纯图片，不显示等级信息）"""
        level_info = result['level_info']
        selected_level = result['selected_level']
        
        # 检查文件是否存在
        if not level_info['exists']:
            await handler.send_text(
                f"❌ 武器图片文件不存在\n"
                f"📁 文件路径: {level_info['file_path']}"
            )
            return
        
        # 使用新方法发送图片
        bot_logger.info(f"正在发送武器图片: {weapon_data['name']} Lv.{selected_level}")
        success = await handler.send_image_from_path(level_info['file_path'])
        
        if success:
            bot_logger.info(f"武器查询成功: {weapon_data['name']} Lv.{selected_level}")
        else:
            await handler.send_text(f"❌ 图片发送失败: {weapon_data['name']}")
    
    async def _send_weapon_list(self, handler: MessageHandler):
        """发送武器列表"""
        try:
            weapons = self.resource_manager.list_resources('weapons')
            
            if not weapons:
                await handler.send_text("📭 暂无可用武器")
                return
            
            # 构建武器列表
            message = "🔫 ARC Raiders 武器列表\n"
            message += "━━━━━━━━━━━━━━━\n"
            
            for weapon in weapons:
                message += f"• {weapon['name']}"
                
                # 显示别名
                if weapon['aliases']:
                    aliases_str = '、'.join(weapon['aliases'][:2])
                    message += f" ({aliases_str})"
                
                message += "\n"
            
            message += "\n━━━━━━━━━━━━━━━\n"
            message += "💡 使用 /weapon <武器名称> 查询详情"
            
            await handler.send_text(message)
            
        except Exception as e:
            bot_logger.error(f"获取武器列表失败: {e}", exc_info=True)
            await handler.send_text("❌ 获取列表失败，请稍后重试")
    
    async def _send_usage(self, handler: MessageHandler):
        """发送使用说明"""
        usage = (
            "🔫 武器查询命令\n"
            "━━━━━━━━━━━━━━━\n"
            "📖 使用方法:\n"
            "• /weapon <武器名称> - 查询武器\n"
            "• /weapon <武器名称> <等级> - 查询指定等级\n"
            "• /weapon list - 查看所有武器\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 示例: /weapon 示例武器"
        )
        await handler.send_text(usage)


