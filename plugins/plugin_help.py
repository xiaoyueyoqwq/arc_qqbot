# -*- coding: utf-8 -*-
"""
帮助插件 - SDK 示例插件
展示了如何创建一个基本的命令处理插件
"""
import sys
import os

# 确保正确的路径设置
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)

# 添加项目根目录到路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.plugin import Plugin, on_command
from utils.message_handler import MessageHandler
from utils.logger import bot_logger

class HelpPlugin(Plugin):
    """
    帮助插件
    
    这是一个示例插件，展示了如何：
    1. 继承 Plugin 基类
    2. 使用 @on_command 装饰器注册命令
    3. 处理消息并发送回复
    """
    
    def __init__(self):
        super().__init__()
        
    @on_command("help", "显示可用命令列表")
    async def handle_help(self, handler: MessageHandler, content: str):
        """
        处理 /help 命令，显示所有可用命令
        
        Args:
            handler: 消息处理器
            content: 命令内容
        """
        bot_logger.info(f"用户 {handler.user_id} 请求帮助信息")
        
        # 从插件管理器获取所有命令
        if self._plugin_manager:
            commands = self._plugin_manager.get_command_list()
            if commands:
                cmd_list = "\n".join([f"▎/{cmd} - {info['description']}" 
                                     for cmd, info in commands.items()])
            else:
                cmd_list = "▎暂无可用命令"
        else:
            cmd_list = "▎/help - 显示此帮助信息"
        
        help_message = (
            "\n🎮 ARC Raiders 查询机器人\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "▎可用命令:\n"
            f"{cmd_list}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "▎📖 命令详解:\n"
            "▎• /map - 查询地图信息和图片\n"
            "▎• /weapon <名称> [等级] - 查询武器（默认1级）\n"
            "▎• /arc - 查询游戏相关信息\n"
            "▎• /help - 显示本帮助信息\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "▎💡 使用技巧:\n"
            "▎每个命令后可加 list 查看完整列表\n"
            "▎例如: /map list\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🌟 祝你游戏愉快！\n"
        )
        await handler.send_text(help_message)
        bot_logger.info(f"成功为用户 {handler.user_id} 提供帮助信息")
