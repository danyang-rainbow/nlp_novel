import tqdm
import json
import os

output_dir = "/nas/jiangdanyang/data/huameng_with_number/"
fnames = os.listdir('/nas/xd/data/huameng/20200629_novels')
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
                if sent['type'] == 1:
                    content = sent['content'] #if sent['type'] == 1 else '[IMAGE] ' + os.path.basename(sent['content'])
                    print(role_name + '::' + content+" "+sent["nComments"], file=f) # nComments