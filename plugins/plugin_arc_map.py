# -*- coding: utf-8 -*-
"""
ARC Raiders 地图查询插件

提供地图查询功能，用户可以通过名称或别名查询地图信息
"""
import sys
import os

# 确保正确的路径设置
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.plugin import Plugin, on_command
from core.resource_manager import get_resource_manager
from utils.message_handler import MessageHandler
from utils.logger import bot_logger


class ARCMapPlugin(Plugin):
    """
    ARC Raiders 地图查询插件
    
    命令：
    - /map <地图名称> - 查询地图信息并显示地图图片
    - /map list - 列出所有可用地图
    """
    
    def __init__(self):
        super().__init__()
        self.resource_manager = get_resource_manager()
    
    async def on_load(self):
        """插件加载时调用"""
        await super().on_load()
        bot_logger.info(f"[{self.name}] 地图查询插件已加载")
    
    @on_command("map", "查询地图信息")
    async def handle_map(self, handler: MessageHandler, content: str):
        """
        处理 /map 命令
        
        用法：
        /map <地图名称> - 查询指定地图
        /map list - 列出所有地图
        """
        # 提取查询参数
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await self._send_usage(handler)
            return
        
        query = parts[1].strip()
        
        # 列表命令
        if query.lower() in ['list', '列表', '全部']:
            await self._send_map_list(handler)
            return
        
        # 查询地图
        await self._query_map(handler, query)
    
    async def _query_map(self, handler: MessageHandler, query: str):
        """查询并发送地图信息"""
        try:
            # 查找地图资源
            resource = self.resource_manager.find_resource('maps', query)
            
            if not resource:
                await handler.send_text(
                    f"❌ 未找到地图: {query}\n"
                    f"💡 使用 /map list 查看所有可用地图"
                )
                return
            
            # 检查文件是否存在
            if not resource['exists']:
                await handler.send_text(
                    f"❌ 地图图片文件不存在\n"
                    f"📁 文件路径: {resource['file_path']}"
                )
                return
            
            # 发送地图图片
            bot_logger.info(f"正在发送地图图片: {resource['name']}")
            success = await handler.send_image_from_path(resource['file_path'])
            
            if success:
                bot_logger.info(f"地图查询成功: {resource['name']}")
            else:
                await handler.send_text(f"❌ 图片发送失败: {resource['name']}")
            
        except Exception as e:
            bot_logger.error(f"查询地图失败: {e}", exc_info=True)
            await handler.send_text("❌ 查询失败，请稍后重试")
    
    async def _send_map_list(self, handler: MessageHandler):
        """发送地图列表"""
        try:
            maps = self.resource_manager.list_resources('maps')
            
            if not maps:
                await handler.send_text("📭 暂无可用地图")
                return
            
            message = "🗺️ ARC Raiders 地图列表\n"
            message += "━━━━━━━━━━━━━━━\n"
            
            for i, map_info in enumerate(maps, 1):
                message += f"{i}. {map_info['name']}"
                
                # 显示别名
                if map_info['aliases']:
                    aliases_str = '、'.join(map_info['aliases'][:3])
                    message += f" ({aliases_str})"
                
                message += "\n"
            
            message += "━━━━━━━━━━━━━━━\n"
            message += "💡 使用 /map <地图名称> 查询详情"
            
            await handler.send_text(message)
            
        except Exception as e:
            bot_logger.error(f"获取地图列表失败: {e}", exc_info=True)
            await handler.send_text("❌ 获取列表失败，请稍后重试")
    
    async def _send_usage(self, handler: MessageHandler):
        """发送使用说明"""
        usage = (
            "🗺️ 地图查询命令\n"
            "━━━━━━━━━━━━━━━\n"
            "📖 使用方法:\n"
            "• /map <地图名称> - 查询地图\n"
            "• /map list - 查看所有地图\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 示例: /map 示例地图"
        )
        await handler.send_text(usage)

