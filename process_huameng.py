import json
import os


def is_cjk_char(char):
    return '\u4e00' <= char <= '\u9fff'

def is_chapter_name(line):
    b = '::' not in line or  line.split( # jdy changed
    )[0][0] == '第' and (line.split()[0][-1] == '话' or line.split()[0][-1] == '章')   # '第23话' or '第45话 回家'
    # if line.startswith('第6话'): assert b, line
    # xx公寓
    return b

def filter_lines(lines, keep_chapter_name=True):
    ret_lines = []
    for line in lines:
        if '::' not in line:
            assert is_chapter_name(line), line
            if keep_chapter_name:
                ret_lines.append(line)
            continue
        speaker, speech = line.split('::', maxsplit=1)
        if speaker.startswith('旁白'):
            if any(s in speech for s in ['正文', '本章完', '待续', '未完', '分割线', '卡文']) or \
                all(not is_cjk_char(c) or c == '卡' for c in speech) and any(c == '卡' for c in speech):
                continue
            if speech.strip() == '':
                continue
        ret_lines.append(line)
    return ret_lines

output_dir = "/nas/jiangdanyang/data/huameng_with_number/"
fnames = os.listdir('/nas/xd/data/huameng/20200629_novels')
image_text_file = "/nas/jiangdanyang/data/final_result.json"
imageinfo = json.load(open(image_text_file))
for fname in fnames:
    d = json.load(open("/nas/xd/data/huameng/20200629_novels/"+fname))
    global_roleId2name = {i['id']: i['name'] for i in d['rolelist']}
    chapter_ids = set()
    output_pathname = output_dir + fname.replace('.json', '.txt')
    with open(output_pathname, 'w') as f:
        for chapter in d['chapters']:
            if chapter['chapter_id'] in chapter_ids: continue
            chapter_ids.add(chapter['chapter_id'])

            print(chapter['chapter_num'], file=f)
            # special_roles += [i for i in chapter['role_list'] if i['capacity'] not in [2, 3]]
            roleId2name = {i['roleId']: i['nickname'] for i in chapter['role_list']}
            for sent in chapter['sentence_list']:
                role_id = sent['roleId']
                if role_id in roleId2name:
                    role_name = roleId2name[role_id]
                elif role_id in global_roleId2name:
                    role_name = global_roleId2name[role_id]
                    print(d['book_name'], role_name, 'in global')
                else:
                    role_name = 'None'
                    print(d['book_name'], role_name, 'not found')
                assert sent['type'] in [1, 2], str(sent['type'])


                if sent['type'] != 1 and os.path.basename(sent['content']) in imageinfo.keys():
                    imagetext = imageinfo[os.path.basename(sent['content'])][0]
                else:
                    imagetext = ""
                imagetext = imagetext.replace("||","~")
                if sent['type']!= 1 and imagetext != "":
                    content = sent['content'] if sent['type'] == 1 else '[' + imagetext+']'
                    # newlines = []
                    # newlines.append(role_name + '::' + content)
                    # outlines = filter_lines(newlines)
                    # if len(outlines) != 0:
                    print(role_name + '::' + content + ' ' + sent['nComments'], file=f) # nComments
                elif sent['type'] == 1:
                    content = sent['content']
                    newlines = []
                    newlines.append(role_name + '::' + content)
                    outlines = filter_lines(newlines)
                    if len(outlines) != 0:
                        print(role_name + '::' + content + ' ' + sent['nComments'], file=f) # nComments
