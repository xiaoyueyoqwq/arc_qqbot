# -*- coding: utf-8 -*-
"""
ARC Raiders 信息查询插件

提供游戏相关信息查询功能
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


class ARCInfoPlugin(Plugin):
    """
    ARC Raiders 信息查询插件
    
    命令：
    - /arc <关键词> - 查询ARC相关信息
    - /arc list - 列出所有可用信息
    """
    
    def __init__(self):
        super().__init__()
        self.resource_manager = get_resource_manager()
    
    async def on_load(self):
        """插件加载时调用"""
        await super().on_load()
        bot_logger.info(f"[{self.name}] ARC信息查询插件已加载")
    
    @on_command("arc", "查询ARC Raiders相关信息")
    async def handle_arc(self, handler: MessageHandler, content: str):
        """
        处理 /arc 命令
        
        用法：
        /arc <关键词> - 查询指定信息
        /arc list - 列出所有信息
        """
        # 提取查询参数
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await self._send_usage(handler)
            return
        
        query = parts[1].strip()
        
        # 列表命令
        if query.lower() in ['list', '列表', '全部']:
            await self._send_info_list(handler)
            return
        
        # 查询信息
        await self._query_info(handler, query)
    
    async def _query_info(self, handler: MessageHandler, query: str):
        """查询并发送ARC信息"""
        try:
            # 查找资源
            resource = self.resource_manager.find_resource('arc', query)
            
            if not resource:
                await handler.send_text(
                    f"❌ 未找到相关信息: {query}\n"
                    f"💡 使用 /arc list 查看所有可用信息"
                )
                return
            
            # 检查文件是否存在
            if not resource['exists']:
                await handler.send_text(
                    f"❌ 信息图片文件不存在\n"
                    f"📁 文件路径: {resource['file_path']}"
                )
                return
            
            # 发送信息图片
            bot_logger.info(f"正在发送ARC信息图片: {resource['name']}")
            success = await handler.send_image_from_path(resource['file_path'])
            
            if success:
                bot_logger.info(f"ARC信息查询成功: {resource['name']}")
            else:
                await handler.send_text(f"❌ 图片发送失败: {resource['name']}")
            
        except Exception as e:
            bot_logger.error(f"查询ARC信息失败: {e}", exc_info=True)
            await handler.send_text("❌ 查询失败，请稍后重试")
    
    async def _send_info_list(self, handler: MessageHandler):
        """发送信息列表"""
        try:
            info_list = self.resource_manager.list_resources('arc')
            
            if not info_list:
                await handler.send_text("📭 暂无可用信息")
                return
            
            message = "🎮 ARC Raiders 信息列表\n"
            message += "━━━━━━━━━━━━━━━\n"
            
            for i, info in enumerate(info_list, 1):
                message += f"{i}. {info['name']}"
                
                # 显示别名
                if info['aliases']:
                    aliases_str = '、'.join(info['aliases'][:3])
                    message += f" ({aliases_str})"
                
                message += "\n"
            
            message += "━━━━━━━━━━━━━━━\n"
            message += "💡 使用 /arc <关键词> 查询详情"
            
            await handler.send_text(message)
            
        except Exception as e:
            bot_logger.error(f"获取ARC信息列表失败: {e}", exc_info=True)
            await handler.send_text("❌ 获取列表失败，请稍后重试")
    
    async def _send_usage(self, handler: MessageHandler):
        """发送使用说明"""
        usage = (
            "🎮 ARC Raiders 信息查询\n"
            "━━━━━━━━━━━━━━━\n"
            "📖 使用方法:\n"
            "• /arc <关键词> - 查询信息\n"
            "• /arc list - 查看所有信息\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 示例: /arc 介绍"
        )
        await handler.send_text(usage)

