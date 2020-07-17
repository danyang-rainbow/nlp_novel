import json
import codecs
import os

# 还是整理一下huameng，kuaidian这俩数据的处理吧
# 首先是huangmeng，我刚刚弄得这个，humeng的原始数据在/nas/xd/data/huameng/20200629_novels/
# 然后是image和txt的ocr数据是/nas/jiangdanyang/data/final_result.json
# 然后是模型


# 首先，肖老师说的那个，只用一个数据，带评论数的huameng数据，然后跑出来的话，无论如何都是没有评论数的，后续还是需要加上评论数。\
# ok,既然你说可以，那就再试试