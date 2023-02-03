import datetime
import hashlib
import json

from tortoise import Model, fields
from tortoise.contrib.mysql.indexes import FullTextIndex


# class BVideo(Model):
#     # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/video/info.md
#     aid = fields.IntField(unique=True, describe='视频aid', index=True)
#     bvid = fields.CharField(max_length=128, describe='视频bvid', index=True)
#     status = fields.IntField(default=0, describe='视频状态code', null=True, index=True)
#     state = fields.IntField(default=0, describe='视频状态state', null=True, index=True)
#     tname = fields.CharField(max_length=128, describe='视频分区', null=True, default='', index=True)
#     pic = fields.TextField(describe='封面', null=True, default='')
#     title = fields.CharField(max_length=256, describe='视频标题', null=True, index=True)
#     publish_time = fields.DatetimeField(default=None, null=True, describe='视频发布时间', index=True)
#     ctime = fields.DatetimeField(default=None, null=True, describe='用户投稿时间', index=True)
#     mission_id = fields.IntField(default=0, describe='稿件参与的活动id', index=True)
#     description = fields.TextField(describe='视频描述', null=True, default='')
#     duration = fields.IntField(describe='视频时长', default=0, index=True)
#     owner_uid = fields.CharField(describe='视频作者UID', null=True, default='0', max_length=128, index=True)
#     owner_name = fields.CharField(max_length=128, describe='视频作者名称', null=True, default='', index=True)
#     staff_list = fields.JSONField(default='[]', describe='合作方mid列表,正序', null=True)
#     view_count = fields.IntField(default=0, describe='播放数', index=True)
#     danmaku_count = fields.IntField(default=0, describe='弹幕数', index=True)
#     reply_count = fields.IntField(default=0, describe='评论数', index=True)
#     like_count = fields.IntField(default=0, describe='视频点赞数', index=True)
#     coin_count = fields.IntField(default=0, describe='投币数', index=True)
#     favorite_count = fields.IntField(default=0, describe='收藏数', index=True)
#     share_count = fields.IntField(default=0, describe='分享数', index=True)
#     now_rank = fields.IntField(default=0, describe='当前排名', index=True)
#     history_rank = fields.IntField(default=0, describe='历史最高排名', index=True)
#     part_count = fields.IntField(default=1, describe='视频分P数', index=True)
#     part_content = fields.JSONField(default="[]", describe='分P视频信息', null=True)
#     tags = fields.JSONField(default='[]', describe='视频标签', null=True)
#     r_hot_rank = fields.CharField(default='', describe='分区排名', max_length=32, null=True, index=True)
#     hash = fields.CharField(max_length=256, describe='hash', null=True, index=True)
#     p_level = fields.IntField(default=0, describe='优先级', index=True)
#     arc = fields.IntField(default=0, describe='arc', index=True)
#     created_at = fields.DatetimeField(null=True, auto_now_add=True, index=True)
#     modified_at = fields.DatetimeField(null=True, auto_now=True, index=True)

#     @staticmethod
#     def _create_hash(
#         aid,
#         bvid,
#         status,
#         state,
#         tname,
#         pic,
#         title,
#         publish_time,
#         ctime,
#         mission_id,
#         description,
#         duration,
#         staff_list,
#         view_count,
#         danmaku_count,
#         reply_count,
#         like_count,
#         coin_count,
#         favorite_count,
#         share_count,
#         now_rank,
#         history_rank,
#         part_count,
#         tags,
#         part_content,
#         r_hot_rank,
#         **kwargs,
#     ):
#         raw = f'{aid}|{bvid}|{status}|{state}|{tname}|{pic}|{title}|{publish_time if publish_time is None else publish_time.strftime("%Y-%m-%d %H:%M:%S")}|{ctime if ctime is None else ctime.strftime("%Y-%m-%d %H:%M:%S")}|{mission_id}|{description}|{duration}|{json.dumps(staff_list)}|{view_count}|{danmaku_count}|{reply_count}|{like_count}|{coin_count}|{favorite_count}|{share_count}|{now_rank}|{history_rank}|{part_count}|{json.dumps(tags)}|{json.dumps(part_content)}|{r_hot_rank}'
#         return hashlib.sha1(raw.encode('utf-8')).hexdigest()

#     async def save(self, *args, **kwargs):
#         self.hash = BVideo._create_hash(
#             self.aid,
#             self.bvid,
#             self.status,
#             self.state,
#             self.tname,
#             self.pic,
#             self.title,
#             self.publish_time,
#             self.ctime,
#             self.mission_id,
#             self.description,
#             self.duration,
#             self.staff_list,
#             self.view_count,
#             self.danmaku_count,
#             self.reply_count,
#             self.like_count,
#             self.coin_count,
#             self.favorite_count,
#             self.share_count,
#             self.now_rank,
#             self.history_rank,
#             self.part_count,
#             self.tags,
#             self.part_content,
#             self.r_hot_rank,
#         )

#         await super().save(*args, **kwargs)

#     class Meta:
#         table = 'bili_video'
#         unique_together = ("aid", "bvid")
#         indexes = [
#             # FullTextIndex(fields={"staff_list"}, parser_name="ngram"),
#             FullTextIndex(fields={"pic"}, parser_name="ngram"),
#             FullTextIndex(fields={"description"}, parser_name="ngram"),
#             # FullTextIndex(fields={"part_content"}, parser_name="ngram"),
#             # FullTextIndex(fields={"tags"}, parser_name="ngram"),
#         ]


# class BUser(Model):
#     # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/user/info.md
#     uid = fields.CharField(pk=True, describe='用户uid', max_length=128, index=True)
#     name = fields.CharField(max_length=128, describe='用户名', null=True, default='', index=True)
#     sex = fields.CharField(max_length=16, describe='性别', null=True, default='', index=True)
#     face = fields.CharField(max_length=256, describe='用户头像', default='', index=True)
#     sign = fields.CharField(max_length=512, describe='用户签名', default='', index=True)
#     birthday = fields.CharField(max_length=32, describe='生日 MM-DD', default='', index=True)
#     rank = fields.IntField(describe='用户Rank', default=0, index=True)
#     level = fields.IntField(describe='用户等级', default=0, index=True)
#     jointime = fields.DatetimeField(default=None, null=True, describe='用户加入时间', index=True)
#     silence = fields.BooleanField(default=False, describe='用户封禁状态,0正常1被封', index=True)
#     live_room_id = fields.IntField(default=0, describe='用户直播间id,0表示不存在直播间', index=True)
#     school = fields.CharField(max_length=128, default='', null=True, describe='用户学校', index=True)
#     fans_count = fields.IntField(default=0, describe='粉丝数', index=True)
#     attention_count = fields.IntField(default=0, describe='关注数', index=True)
#     is_senior_member = fields.BooleanField(default=False, describe='是否是硬核会员', index=True)
#     province = fields.CharField(describe='IP省份', null=True, default='', max_length=32, index=True)
#     mcn = fields.CharField(describe='mcn名称', null=True, default='', max_length=32, index=True)
#     user_p = fields.IntField(default=3, describe='用户基础信息优先级', index=True)
#     user_data_p = fields.IntField(default=3, describe='用户一级信息优先级', index=True)
#     post_data_p = fields.IntField(default=3, describe='投稿信息优先级', index=True)

#     hash = fields.CharField(max_length=256, describe='hash', index=True)
#     created_at = fields.DatetimeField(null=True, auto_now_add=True, index=True)
#     modified_at = fields.DatetimeField(null=True, auto_now=True, index=True)

#     @staticmethod
#     def _create_hash(
#         uid,
#         name,
#         sex,
#         face,
#         sign,
#         birthday,
#         rank,
#         level,
#         silence,
#         live_room_id,
#         school,
#         fans_count,
#         attention_count,
#         is_senior_member,
#         province,
#         mcn,
#         **kwargs,
#     ):
#         raw = f'{uid}|{name}|{sex}|{face}|{sign}|{birthday}|{rank}|{level}|{silence}|{live_room_id}|{school}|{fans_count}|{attention_count}|{is_senior_member}|{province}|{mcn}'

#         return hashlib.sha1(raw.encode('utf-8')).hexdigest()

#     async def save(self, *args, **kwargs):
#         self.hash = BUser._create_hash(
#             self.uid,
#             self.name,
#             self.sex,
#             self.face,
#             self.sign,
#             self.birthday,
#             self.rank,
#             self.level,
#             self.silence,
#             self.live_room_id,
#             self.school,
#             self.fans_count,
#             self.attention_count,
#             self.is_senior_member,
#             self.province,
#             self.mcn,
#         )
#         await super().save(*args, **kwargs)

#     class Meta:
#         table = 'bili_user'


# class BComment(Model):
#     # https://github.com/SocialSisterYi/bilibili-API-collect/tree/master/comment
#     rpid = fields.CharField(pk=True, max_length=128, describe='评论ID', unique=True, index=True)
#     type = fields.IntField(describe='评论类型代码', index=True)
#     oid = fields.CharField(max_length=64, describe='目标ID, oid', index=True)
#     uid = fields.CharField(describe='评论者UID, 对应mid', null=True, default='', max_length=128, index=True)
#     uname = fields.CharField(max_length=128, describe='评论者名称', index=True)
#     root = fields.CharField(describe='回复的评论ID', null=True, default='', max_length=64, index=True)
#     parent = fields.CharField(describe='上层楼的评论rpid', null=True, default='', max_length=64, index=True)
#     dialog = fields.CharField(describe='对话根rpid', null=True, default='', max_length=64, index=True)
#     like_count = fields.IntField(describe='点赞数', default=0, index=True)
#     ctime = fields.DatetimeField(describe='评论时间', default=None, null=True, index=True)
#     content = fields.TextField(describe='评论内容')
#     device = fields.CharField(describe='评论发送平台设备', null=True, default='', max_length=128, index=True)
#     plat = fields.IntField(describe='评论发送端', default=0, null=True, index=True)
#     province = fields.CharField(describe='评论者IP省份', null=True, default='', max_length=32, index=True)
#     up_top = fields.BooleanField(describe='UP是否置顶', default=False, index=True)
#     up_like = fields.BooleanField(describe='UP是否点赞', default=False, index=True)
#     up_reply = fields.BooleanField(describe='UP是否回复', default=False, index=True)
#     created_at = fields.DatetimeField(null=True, auto_now_add=True, index=True)
#     modified_at = fields.DatetimeField(null=True, auto_now=True, index=True)

#     class Meta:
#         table = 'bili_comment'
#         indexes = [
#             FullTextIndex(fields={"content"}, parser_name="ngram"),
#         ]


# class BDynamic(Model):
#     # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/dynamic/get_dynamic_detail.md
#     id = fields.CharField(pk=True, max_length=128, describe='动态dynamic_id_str', index=True)
#     status = fields.IntField(describe='动态状态', default=0, null=True, index=True)
#     type = fields.IntField(describe='动态类型', default=0, index=True)
#     rid = fields.CharField(describe='动态rid', default=0, null=True, max_length=128, index=True)
#     owner_uid = fields.CharField(default='0', max_length=128, null=True, describe='作者uid', index=True)
#     owner_name = fields.CharField(max_length=128, describe='作者昵称', default='', null=True, index=True)
#     view_count = fields.IntField(default=0, describe='查看数', index=True)
#     repost_count = fields.IntField(default=0, describe='转发数', index=True)
#     comment_count = fields.IntField(default=0, describe='评论数', index=True)
#     like_count = fields.IntField(default=0, describe='点赞数', index=True)
#     dynamic_id = fields.CharField(max_length=128, describe='动态id,不知道有啥用', default='', null=True, index=True)
#     publish_time = fields.DatetimeField(default=None, null=True, describe='发布时间', index=True)
#     pre_dy_id = fields.CharField(max_length=128, null=True, default='0', describe='前一个动态id, 多层转发时的上一个dynamic_id_str', index=True)
#     orig_dy_id = fields.CharField(max_length=128, null=True, default='0', describe='源动态id, 转发的原始dynamic_id_str', index=True)
#     orig_type = fields.IntField(default=0, describe='原动态类型', index=True)
#     content = fields.TextField(describe='动态内容', default='', null=True)
#     card_json = fields.JSONField(default="{}", null=True, describe='动态CARD数据, 不计入去重')
#     doc_id = fields.BigIntField(describe='相册ID,type=2时取card_json.item.id', default=0, null=True, index=True)
#     add_on_card_info = fields.JSONField(default="[]", null=True, describe='动态Add数据, 不计入去重')
#     hash = fields.CharField(max_length=128, describe='动态hash', index=True)
#     p_level = fields.IntField(default=0, describe='优先级', index=True)
#     created_at = fields.DatetimeField(null=True, auto_now_add=True, index=True)
#     modified_at = fields.DatetimeField(null=True, auto_now=True, index=True)

#     @staticmethod
#     def _create_hash(
#         id,
#         status,
#         type,
#         rid,
#         owner_uid,
#         owner_name,
#         view_count,
#         repost_count,
#         comment_count,
#         like_count,
#         dynamic_id,
#         publish_time,
#         pre_dy_id,
#         orig_dy_id,
#         orig_type,
#         content,
#         **kwargs,
#     ):
#         raw = f'{id}|{status}|{type}|{rid}|{owner_uid}|{owner_name}|{view_count}|{repost_count}|{comment_count}|{like_count}|{dynamic_id}|{publish_time if publish_time is None else publish_time.strftime("%Y-%m-%d %H:%M:%S")}|{pre_dy_id}|{orig_dy_id}|{orig_type}|{content}'
#         return hashlib.sha1(raw.encode('utf-8')).hexdigest()

#     async def save(self, *args, **kwargs):
#         self.hash = BDynamic._create_hash(
#             self.id,
#             self.status,
#             self.type,
#             self.rid,
#             self.owner_uid,
#             self.owner_name,
#             self.view_count,
#             self.repost_count,
#             self.comment_count,
#             self.like_count,
#             self.dynamic_id,
#             self.publish_time,
#             self.pre_dy_id,
#             self.orig_dy_id,
#             self.orig_type,
#             self.content,
#         )
#         await super().save(*args, **kwargs)

#     class Meta:
#         table = 'bili_dynamic'
#         indexes = [
#             FullTextIndex(fields={"content"}, parser_name="ngram"),
#             # FullTextIndex(fields={"card_json"}, parser_name="ngram"),
#             # FullTextIndex(fields={"add_on_card_info"}, parser_name="ngram"),
#         ]


# class ChangeLog(Model):
#     id = fields.IntField(pk=True, index=True)
#     table_name = fields.CharField(max_length=128, describe='表名', index=True)
#     column_key = fields.CharField(max_length=128, describe='索引字段名', index=True)
#     column_value = fields.CharField(max_length=128, describe='索引字段值', index=True)
#     changed_key = fields.CharField(max_length=128, describe='变化字段名', index=True)
#     old_content = fields.TextField(describe='原值', null=True)
#     new_content = fields.TextField(describe='新值', null=True)

#     created_at = fields.DatetimeField(null=True, auto_now_add=True, index=True)
#     modified_at = fields.DatetimeField(null=True, auto_now=True, index=True)

#     class Meta:
#         table = 'change_log'
#         indexes = [
#             FullTextIndex(fields={"old_content"}, parser_name="ngram"),
#             FullTextIndex(fields={"new_content"}, parser_name="ngram"),
#         ]


# class JobResult(Model):
#     id = fields.CharField(pk=True, max_length=128, describe='任务id, sha1(func, args, timestamp)')
#     name = fields.CharField(max_length=128, describe='任务名', index=True)
#     type = fields.CharField(max_length=128, describe='任务类型分类', index=True)
#     status = fields.IntField(describe='任务状态', null=True, index=True)
#     message = fields.TextField(default='', describe='任务结果', null=True)
#     created_at = fields.DatetimeField(null=True, auto_now_add=True, index=True)

#     class Meta:
#         table = 'job_result'
#         indexes = [
#             FullTextIndex(fields={"message"}, parser_name="ngram"),
#         ]
