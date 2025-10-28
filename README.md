# ARC Raiders QQ Bot 🤖

| 一个基于插件化架构的 ARC Raiders 游戏查询机器人，支持地图、武器、游戏信息查询。

## ✨ 功能特性

| **地图查询** - `/map <地图名称>` 查询地图信息和图片
| **武器查询** - `/weapon <武器名称> [等级]` 查询武器数据，支持等级系统
| **游戏信息** - `/arc <关键词>` 查询游戏相关信息
| **帮助信息** - `/help` 显示所有可用命令

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置机器人

```bash
# 复制配置模板
cp config/config.yaml.example config/config.yaml

# 编辑配置文件，填入你的机器人信息
# - appid: 机器人 APPID
# - token: 机器人 Token
# - secret: 机器人 Secret
```

### 3. 启动 Redis

```bash
redis-server
```

### 4. 运行机器人

```bash
# 正式运行
python bot.py

# 本地测试（无需真实QQ Bot）
python bot.py -local
# 访问 http://127.0.0.1:8080 进行测试
```

## 📦 添加资源

### 添加地图

| **1. 添加图片** - 将地图图片放入 `resources/maps/` 目录
| **2. 编辑索引** - 在 `resources/maps.json` 中添加：

```json
{
  "地图名称": {
    "name": "显示名称",
    "filename": "map.png",
    "aliases": ["别名1", "别名2"]
  }
}
```

### 添加武器

| **1. 添加图片** - 将武器图片放入 `resources/weapons/` 目录
| **2. 编辑索引** - 在 `resources/weapons.json` 中添加：

```json
{
  "武器名称": {
    "name": "显示名称",
    "aliases": ["别名1", "别名2"],
    "levels": {
      "1": {"filename": "weapon_lv1.png"},
      "2": {"filename": "weapon_lv2.png"},
      "3": {"filename": "weapon_lv3.png"}
    }
  }
}
```

### 添加游戏信息

| **1. 添加图片** - 将信息图片放入 `resources/arc/` 目录
| **2. 编辑索引** - 在 `resources/arc.json` 中添加：

```json
{
  "信息标题": {
    "name": "显示名称",
    "filename": "info.png",
    "aliases": ["别名1", "别名2"]
  }
}
```

## 🔧 项目结构

```
arc_qqbot/
├── bot.py                      # 主入口
├── config/
│   └── config.yaml.example     # 配置模板
├── core/                       # 核心服务
│   ├── image_uploader.py       # 图片上传
│   ├── resource_manager.py     # 资源管理
│   └── plugin.py               # 插件系统
├── plugins/                    # 功能插件
│   ├── plugin_arc_map.py       # 地图查询
│   ├── plugin_arc_weapon.py    # 武器查询
│   ├── plugin_arc_info.py      # 信息查询
│   └── plugin_help.py          # 帮助信息
└── resources/                  # 游戏资源
    ├── maps/                   # 地图图片
    ├── weapons/                # 武器图片
    ├── arc/                    # 信息图片
    ├── maps.json               # 地图索引
    ├── weapons.json            # 武器索引
    └── arc.json                # 信息索引
```

## 💡 使用示例

### 地图查询

```
用户: /map 示例地图
机器人: 
| 🗺️ 示例地图
| ━━━━━━━━━━━━━━━
| 📝 这是一个示例地图
| ━━━━━━━━━━━━━━━
| 🔗 查看地图: [图片链接]
```

### 武器查询

```
用户: /weapon 示例武器
机器人:
| 🔫 示例武器
| ━━━━━━━━━━━━━━━
| 🔗 查看武器: [图片链接]

用户: /weapon 示例武器 2
机器人:
| 🔫 示例武器
| ━━━━━━━━━━━━━━━
| 🔗 查看武器: [图片链接]
```

| 💡 **说明**：
| • 不指定等级时，默认显示1级武器
| • 可通过 `/weapon 武器名 等级` 查询指定等级
| • 纯图片展示，不显示等级提示

## 🛠️ 技术特性

| **插件化设计** - 模块化架构，易于扩展
| **热更新** - 修改资源配置后自动生效，无需重启
| **等级系统** - 支持武器等级查询
| **图片发送** - 本地图片→uapis.cn上传→QQ服务器发送
| **本地测试** - 内置测试工具，方便开发调试

## 📸 图片发送流程

| **1. 本地存储** - 图片保存在 `resources/maps/`, `resources/weapons/`, `resources/arc/`
| **2. API上传** - 使用 uapis.cn API将图片转为Base64上传，获取公开URL
| **3. QQ发送** - 用获取的URL告诉QQ服务器发送图片给用户
| **4. 纯图片** - 用户只看到图片，无文本描述

## 📝 开发插件

| 在 `plugins/` 目录创建新文件，继承 `Plugin` 类：

```python
from core.plugin import Plugin, on_command
from utils.message_handler import MessageHandler

class MyPlugin(Plugin):
    @on_command("hello", "打招呼")
    async def handle_hello(self, handler: MessageHandler, content: str):
        await handler.send_text("你好！")
```

| 重启机器人后，插件会自动加载。

## 📄 许可证

| 本项目采用 **CC BY-NC-SA 4.0** 许可证
| 
| **许可证要点：**
| ✅ 可自由分享和修改
| ✅ 必须署名原作者
| ❌ 禁止商业用途
| ✅ 相同方式共享
|
| 详细信息请查看 [LICENSE](LICENSE) 文件

---

| 🎮 **祝你游戏愉快！**
| 📧 **问题反馈**: [GitHub Issues](https://github.com/xiaoyueyoqwq/arc_qqbot/issues)
| ⭐ **喜欢的话请给个 Star！**
