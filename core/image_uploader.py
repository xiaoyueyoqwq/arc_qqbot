# -*- coding: utf-8 -*-
"""
图片上传服务 - 使用第三方API上传图片

通过 Base64 编码将图片上传到 uapis.cn，获取公网可访问的URL
"""
import base64
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from utils.logger import bot_logger


class ImageUploader:
    """图片上传服务类"""
    
    # uapis.cn 图片上传API
    UPLOAD_API_URL = "https://uapis.cn/api/v1/image/frombase64"
    
    def __init__(self, timeout: int = 30):
        """
        初始化图片上传服务
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
    
    async def upload_image_from_path(self, image_path: str | Path) -> Optional[str]:
        """
        从文件路径上传图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: 图片URL，失败返回None
        """
        try:
            image_path = Path(image_path)
            
            # 检查文件是否存在
            if not image_path.exists():
                bot_logger.error(f"图片文件不存在: {image_path}")
                return None
            
            # 检查文件大小（限制10MB）
            file_size = image_path.stat().st_size
            if file_size > 10 * 1024 * 1024:
                bot_logger.error(f"图片文件过大: {file_size / 1024 / 1024:.2f}MB > 10MB")
                return None
            
            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 上传图片
            return await self.upload_image_from_bytes(image_data, image_path.suffix)
            
        except Exception as e:
            bot_logger.error(f"从路径上传图片失败: {e}", exc_info=True)
            return None
    
    async def upload_image_from_bytes(
        self, 
        image_bytes: bytes, 
        file_extension: str = ".png"
    ) -> Optional[str]:
        """
        从字节数据上传图片
        
        Args:
            image_bytes: 图片字节数据
            file_extension: 文件扩展名（用于确定MIME类型）
            
        Returns:
            str: 图片URL，失败返回None
        """
        try:
            # 确定MIME类型
            mime_type = self._get_mime_type(file_extension)
            
            # 转换为Base64
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # 构造Data URI
            data_uri = f"data:{mime_type};base64,{base64_data}"
            
            # 上传图片
            return await self._upload_to_api(data_uri)
            
        except Exception as e:
            bot_logger.error(f"从字节上传图片失败: {e}", exc_info=True)
            return None
    
    async def _upload_to_api(self, data_uri: str) -> Optional[str]:
        """
        调用API上传图片
        
        Args:
            data_uri: Base64 Data URI
            
        Returns:
            str: 图片URL，失败返回None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.UPLOAD_API_URL,
                    json={"imageData": data_uri}
                )
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    bot_logger.error(
                        f"图片上传失败，HTTP状态码: {response.status_code}, "
                        f"响应: {response.text}"
                    )
                    return None
                
                # 解析响应
                result = response.json()
                
                # 检查业务状态码
                if result.get('code') != 200:
                    bot_logger.error(f"图片上传失败: {result.get('msg', '未知错误')}")
                    return None
                
                # 获取图片URL
                image_url = result.get('image_url')
                if not image_url:
                    bot_logger.error("响应中缺少图片URL")
                    return None
                
                bot_logger.info(f"图片上传成功: {image_url}")
                return image_url
                
        except httpx.TimeoutException:
            bot_logger.error(f"图片上传超时（{self.timeout}秒）")
            return None
        except httpx.RequestError as e:
            bot_logger.error(f"图片上传请求失败: {e}")
            return None
        except Exception as e:
            bot_logger.error(f"图片上传异常: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _get_mime_type(file_extension: str) -> str:
        """
        根据文件扩展名获取MIME类型
        
        Args:
            file_extension: 文件扩展名（如 .png, .jpg）
            
        Returns:
            str: MIME类型
        """
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        
        extension = file_extension.lower()
        return mime_types.get(extension, 'image/png')


# 全局单例
_image_uploader_instance: Optional[ImageUploader] = None


def get_image_uploader() -> ImageUploader:
    """
    获取图片上传服务单例
    
    Returns:
        ImageUploader: 图片上传服务实例
    """
    global _image_uploader_instance
    if _image_uploader_instance is None:
        _image_uploader_instance = ImageUploader()
    return _image_uploader_instance

