from init import app, logger
from handler.base import HandlerBase


class NormalHandler(HandlerBase):
    @classmethod
    async def format2cq(cls, content: dict) -> str:
        result = ''
        if not isinstance(content, dict):
            logger.error(f'content is not dict: {content}')
        if content.get('text'):
            result += content.get('text')
        if result:
            result += '\n' + '\n'.join([f'[CQ:image,file={i},c=3]' for i in content.get('pic', [])])
        # logger.info(f'[{result}]')
        result = result.strip('\n')
        return result

    @classmethod
    async def new_handler(cls, handler: str, store: str, store_path, content, handlers: list, *args, **kwargs):
        if handler == 'normal.format2cq':
            content = await cls.format2cq(content)
        else:
            logger.warning(f'unknown handler type: {handler}')
        return content
