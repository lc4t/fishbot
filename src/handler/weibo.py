import json
from init import app
from init import logger
from handler.base import HandlerBase


# class Dynamic:
#     def __init__(self, content: json):
#         self.drop = False
#         self.dynamic_id = content.get('id_str')  # 动态ID
#         self.dynamic_type = content.get('type')  # 动态类型
#         self.username = content.get('modules').get('module_author').get('name')  # 发布者用户名
#         self.uid = content.get('modules').get('module_author').get('mid')  # 发布者UID
#         self.avatar_url = content.get('modules').get('module_author').get('face')  # 发布者头像地址
#         self.text = ''  # 本动态原创的文字内容
#         self.pic = []  # 本动态原创的图片地址
#         self.url = ''  # 跳转稿件地址
#         self.desc = ''  # 稿件简介
#         self.title = ''  # 稿件标题
#         self.orig = None
#         # 其他内容
#         self.additional_type = ''  # 类型
#         self.additional_url = ''  # 对象链接
#         self.additional_text = ''  # 文字描述
#         self.additional_pic = []  # 包含图片
#         self.additional_title = ''  # 标题
#         self.additional_timer = ''  # 时间

#         if content.get('modules').get('module_dynamic').get('desc'):
#             # 文字动态内容
#             self.text = content.get('modules').get('module_dynamic').get('desc').get('text')

#         if self.dynamic_type in ['DYNAMIC_TYPE_FORWARD']:
#             # 转发动态
#             # 转发的动态类型有：DYNAMIC_TYPE_AV
#             self.orig = Dynamic(content.get('orig'))

#         elif self.dynamic_type in ['DYNAMIC_TYPE_WORD', 'DYNAMIC_TYPE_DRAW']:
#             # 文字动态 DYNAMIC_TYPE_WORD
#             # 图文动态 DYNAMIC_TYPE_DRAW

#             additional = content.get('modules').get('module_dynamic').get('additional')
#             if additional:
#                 self.additional_type = additional.get('type')
#                 if self.additional_type in ['ADDITIONAL_TYPE_UGC']:
#                     # 评论投稿并转发
#                     self.additional_url = 'https:' + additional.get('ugc').get('jump_url')
#                     self.additional_title = additional.get('ugc').get('title')
#                     self.additional_pic.append(additional.get('ugc').get('cover'))
#                     # self.pic.append(additional.get('ugc').get('cover'))
#                     # self.text = f'「{self.username}」转发了投稿:\n{self.text}\n原投稿: {title} {url}'
#                 elif self.additional_type in ['ADDITIONAL_TYPE_RESERVE']:
#                     # 预约
#                     self.additional_timer = (
#                         content.get('modules').get('module_dynamic').get('additional').get('reserve').get('desc1').get('text')
#                     )
#                     self.additional_title = content.get('modules').get('module_dynamic').get('additional').get('reserve').get('title')
#                     # self.text = f'「{self.username}」新预约:\n{self.text}\n{title} @{timer}'
#                 else:
#                     logger.error(f'unknown additional type: {additional.get("type")}')
#             else:
#                 pass
#                 # self.text = f'「{self.username}」新动态:\n{self.text}'

#             major = content.get('modules').get('module_dynamic').get('major')
#             if major:
#                 self.pic += [i.get('src') for i in major.get('draw').get('items', [])]
#         elif self.dynamic_type in ['DYNAMIC_TYPE_AV']:
#             # if self.text is None:
#             #     self.text = ''
#             #     logger.info(f'new video without text, jump it')
#             # else:
#             major = content.get('modules').get('module_dynamic').get('major')
#             self.pic.append(major.get('archive').get('cover'))
#             self.desc = major.get('archive').get('desc')
#             self.url = 'https:' + major.get('archive').get('jump_url')
#             self.title = major.get('archive').get('title')
#             # self.text = f'「{self.username}」新投稿:\n{self.text}\n{self.title} 投稿地址: {self.url}\n简介: {self.desc}'
#         elif self.dynamic_type in ['DYNAMIC_TYPE_LIVE_RCMD']:
#             # 正在直播, 忽略
#             self.drop = True
#             pass
#         else:
#             logger.error(f'unknown dynamic type: {self.dynamic_type}')

#     def __str__(self):
#         return f'Dynamic({self.dynamic_id})'

#     def get_result_text(self):
#         if self.dynamic_type in ['DYNAMIC_TYPE_WORD', 'DYNAMIC_TYPE_DRAW']:
#             if self.additional_type in ['ADDITIONAL_TYPE_UGC']:
#                 # 评论了稿件
#                 return f'「{self.username}」评论了稿件:\n{self.text}\n 原投稿: {self.additional_title} {self.additional_url} \n动态链接: https://t.bilibili.com/{self.dynamic_id}'
#             elif self.additional_type in ['ADDITIONAL_TYPE_RESERVE']:
#                 # 预约
#                 return f'「{self.username}」发布了预约:\n{self.text}\n{self.additional_title} @{self.additional_timer} \n动态链接: https://t.bilibili.com/{self.dynamic_id}'
#             else:
#                 assert bool(self.additional_type) == False
#                 return f'「{self.username}」新动态:\n{self.text}\n动态链接: https://t.bilibili.com/{self.dynamic_id}'
#         elif self.dynamic_type in ['DYNAMIC_TYPE_AV']:
#             return f'「{self.username}」新投稿:\n{self.text}\n{self.title} {self.url}\n简介: \n{self.desc} \n动态链接: https://t.bilibili.com/{self.dynamic_id}'
#         elif self.dynamic_type in ['DYNAMIC_TYPE_FORWARD']:
#             return f'「{self.username}」转发了动态:\n{self.text}\n动态链接: https://t.bilibili.com/{self.dynamic_id}'
#         elif self.dynamic_type in ['DYNAMIC_TYPE_LIVE_RCMD']:

#             return ''
#         else:
#             logger.error(f'unknown dynamic type: {self.dynamic_type}')
#         # elif self.dynamic_type in ['DYNAMIC_TYPE_LIVE']:
#         #     return f'「{self.username}」开播了:\n{self.text}\n{self.title} {self.url}\n简介: {self.desc} \n->https://t.bilibili.com/{self.dynamic_id}'

#     def get_result_pic(self):
#         return self.pic


class WeiboDynamicHandler(HandlerBase):
    @staticmethod
    async def split2format(content: json) -> dict:
        uname = content.get('user').get('screen_name')
        uid = content.get('user').get('idstr')
        dynamic_id = content.get('idstr')
        text = content.get('text_raw', '')
        pic_ids = content.get('pic_ids', [])
        pics = []
        for one in pic_ids:
            pics.append(content.get('pic_infos').get(one).get('original').get('url'))
        result = {
            'text': f'「{uname}」新微博: {text}\n原文链接: https://weibo.com/{uid}/{dynamic_id}',
            'pic': pics,
        }
        return result

    @classmethod
    async def new_handler(cls, handler: str, content: json):
        if handler == 'weibo.dynamic.split2format':
            content = await cls.split2format(content)
        else:
            logger.error(f'unknown handler: {handler}')
        return content


class WeiboHandler(HandlerBase):
    @classmethod
    async def new_handler(cls, handler: str, store: str, store_path, content, handlers: list, *args, **kwargs):
        if isinstance(content, str) or isinstance(content, bytes):
            content = json.loads(content)
        if handler.startswith('weibo.dynamic.'):
            content = await WeiboDynamicHandler.new_handler(handler, content)
        else:
            logger.warning(f'unknown handler type: {handler}')
        return content
