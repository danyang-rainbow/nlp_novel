import os
from collections import Counter, defaultdict, OrderedDict
import codecs
from itertools import combinations
import json

novel_source_dir = "/nas/jiangdanyang/scene_cut_datas_convert"
output_dir = "/nas/jiangdanyang/bk2"

def extract_speakers(lines, include_aside=False):
    speakers = defaultdict(int)
    for line in lines:
        if '::' in line:
            speaker = line.split('::')[0]
            if include_aside or speaker != '旁白':
                speakers[speaker] += 1
    speakers = OrderedDict(sorted(speakers.items(), key=lambda x: x[1], reverse=True))
    return speakers

def is_scene_sep(line, bos='::', sep_chars=None):
    if sep_chars is None:
        sep_chars = ['…', '—', '.', '·', '-', '。']
    if bos not in line: return False
    speaker, speech = line.split(bos, maxsplit=1)
    return speaker == '旁白' and all(c in sep_chars for c in speech)

def convert_and_join(lines, bos='：', sep_chars=None, BOS='[unused40]', EOS='[unused41]', SEP='[SEP]'):
    if sep_chars is None:
        sep_chars = ['.']
    joined_lines = []
    for line in lines:
        speaker, speech = line.split(bos, maxsplit=1)
        scene_sep = is_scene_sep(line, bos=bos, sep_chars=sep_chars)
        if len(joined_lines) > 0 and not prev_scene_sep and not scene_sep and prev_speaker == speaker:
            joined_lines[-1][1].append(speech)
        else:
            joined_lines.append([speaker, [speech]])
        prev_speaker, prev_speech, prev_scene_sep = speaker, speech, scene_sep
    joined_lines = [speaker + BOS + SEP.join(speeches) + EOS for speaker, speeches in joined_lines]
    return joined_lines

def sort_speaker_pair(pair, all_speakers):
    pair = sorted(pair, key=lambda x: all_speakers[x], reverse=True) \
        if all_speakers[pair[0]] != all_speakers[pair[1]] else sorted(pair)
    return tuple(pair)

def get_speaker_pairs(speakers, all_speakers, min_speeches=20):
    speakers = [speaker for speaker in speakers if all_speakers[speaker] >= min_speeches]
    return [sort_speaker_pair(pair, all_speakers) for pair in combinations(speakers, 2)]

def join_speakers(speakers0, speakers1):
    for speaker, count in speakers1.items():
        if speaker in speakers0:
            speakers0[speaker] += count
        else:
            speakers0[speaker] = count

def join_adjacent_scenes(scenes, adjacent_scene_sep='==='):
    joined_scenes = []
    for scene in scenes:
        start_idx, end_idx, scene_lines, speakers = scene
        if len(joined_scenes) > 0:
            last_start_idx, last_end_idx, last_scene_lines, last_speakers = joined_scenes[-1]
        if len(joined_scenes) == 0 or last_end_idx < start_idx:
            joined_scenes.append(scene)
        else:
            assert last_end_idx == start_idx, '%d->%d, %d->%d' % (last_start_idx, last_end_idx, start_idx, end_idx)
            start_idx = last_start_idx
            scene_lines = last_scene_lines + ['旁白::' + adjacent_scene_sep] + scene_lines
            join_speakers(last_speakers, speakers)
            joined_scenes[-1] = [start_idx, end_idx, scene_lines, last_speakers]
    return joined_scenes

def join_scenes(scenes, x, name="",scene_sep='...'):
    all_lines = []
    cc = 0
    for scene in scenes:
        x1,x2,x3,x4 = scene
        commentmax = 0
        commentline = ""
        for i, line in enumerate(x3):
            pre_line = x3[i-1] if i-1 >=0 else None
            next_line = x3[i+1] if i+1 < len(x3) else None
            tempx = get_comment_number(pre_line, line, next_line, name,x)
            if  tempx > commentmax:
                commentline = line
                commentmax = tempx
        if len(all_lines) > 0:
            all_lines.append('旁白::' + scene_sep)
        all_lines.append("标题::"+commentline+" "+str(commentmax))
        start_idx, end_idx, scene_lines, speakers = scene
        all_lines += scene_lines
        cc += 1
    if cc <= 2:
        all_lines=[]
    return all_lines

def get_comment_number(line_pre, line, line_next, novel_name, x):
    novel_name = novel_name.split(".")[0]
    dialogs = []
    for novel in x:
        if novel["name"] == novel_name:
            for story in novel["stories"]:
                dialogs.append(story["dialogs"])
    lineitems = line.split("::")
    prelinecontent = line_pre.split("::")[1] if line_pre != None and "::" in line_pre  else None
    nextlinecontent = line_next.split("::")[1] if line_next != None and "::" in line_next else None
    # print(lineitems, novel_name)
    for dialog_set in dialogs:
        for i, dialog in enumerate(dialog_set):
            if( i-1 >0 and i+1 < len(dialog_set) and lineitems[0] == dialog["character"] and lineitems[1] == dialog["content"] and prelinecontent == dialog_set[i-1]["content"] and dialog_set[i+1]["content"] == nextlinecontent):
                # print("comment", dialog["comment_count"])
                return dialog["comment_count"]
    return 0

if __name__ == '__main__':

    # TODO: 数字中间空一格 done
    # TODO：<= 2 done
    # TODO: 以===为分隔 done
    filelist = os.listdir(novel_source_dir)
    fileintput = codecs.open("/nas/xd/data/kuaidian/young_collection_datas.json", encoding='utf-8')
    x = json.load(fileintput)

    for name in filelist:
        if name == "我的哥哥是校草.txt_out.txt" or name == "王默复仇记.txt_out.txt" or name == "高冷小草遇上霸气校花.txt_out.txt":
            continue
        print(name)
        lines = [line.strip() for line in codecs.open(os.path.join(novel_source_dir, name),encoding='utf-8')]

        newlines = []

        for line in lines:
            if line[0] == "#":
                newline = line[line.find("旁"):]
                newlines.append("旁白::===")
                newlines.append(newline)
            else:
                newlines.append(line)

        lines = newlines

        speakers = extract_speakers(lines[:3000], include_aside=True)

        n_scenes = 0
        for speaker in speakers: speakers[speaker] = 0
        print('line', end='\t')
        for speaker in speakers:
            if speaker != '旁白':
                print(speaker, end='\t')
        print()
        for i, line in enumerate(lines[:3000]):
            if '::' in line:
                speaker, speech = line.split('::', maxsplit=1)
                if speaker == '旁白' and all(c in ['…', '.', '·'] for c in speech):
                    print(i, end='\t')
                    for speaker, speech_len in speakers.items():
                        if speaker != '旁白':
                            print('-' * min(7, int(round(speech_len / 10))), end='\t')
                    print()
                    for speaker in speakers: speakers[speaker] = 0
                    n_scenes += 1
                    if n_scenes == 500: break
                else:
                    # if speaker not in speakers: speaker = 'UNK'
                    if speaker in speakers: speakers[speaker] += 1

        # lines = filter_lines(lines) # TODO: filter lines 应该被加入

        scenes = []
        start_idx, end_idx, scene_lines = 0, None, []
        for i, line in enumerate(lines):
            if "旁白::===" in line:
                end_idx = i
                speakers = extract_speakers(scene_lines)
                scenes.append([start_idx, end_idx, scene_lines, speakers])
                start_idx, end_idx, scene_lines = i, None, []
            else:
                scene_lines.append(line)

        all_speakers = extract_speakers(lines, include_aside=True)
        AB_chats = defaultdict(list)
        for scene in scenes:
            start_idx, end_idx, scene_lines, speakers = scene
            speaker_pairs = get_speaker_pairs(speakers, all_speakers)
            for speaker_pair in speaker_pairs:
                AB_chats[speaker_pair].append(scene)

        base, ext = os.path.splitext(name)

        for namea in all_speakers:
            for nameb in all_speakers:
                if namea != nameb:
                    key = (namea, nameb)
                    AB_chat_fname = base + '_' + key[0] + 'vs' + key[1] + ext
                    all_lines = join_scenes(join_adjacent_scenes(AB_chats[key]), x=x, name=base)
                    if len(all_lines) == 0 : continue
                    if "/" in AB_chat_fname: continue
                    with codecs.open(os.path.join(output_dir+'/AB_chats2', AB_chat_fname), mode='w',encoding='utf-8') as f:
                        for line in all_lines:
                            print(line.replace('::', '：'), file=f)