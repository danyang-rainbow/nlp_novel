import codecs
import re
import argparse
import os


def is_chapter_name(line):
    chapter_pattern = re.compile(r'第[0-9零一二三四五六七八九十百千]+章')
    chapter_pattern2 = re.compile(r'^[0-9零一二三四五六七八九十百千]+$')
    chapter_pattern3 = re.compile(r'^[0-9]')
    b = re.search(chapter_pattern, line) is not None or \
        re.search(chapter_pattern2, line) is not None or \
        re.search(chapter_pattern3, line) is not None and not line.endswith('。')
    return b

def is_scene_sep(line, bos='::', sep_chars=None):
    if sep_chars is None:
        sep_chars = ['…', '—', '.', '·', '-', '。']
    if bos not in line: return False
    speaker, speech = line.split(bos, maxsplit=1)
    return speaker == '旁白' and all(c in sep_chars for c in speech)

def processf(lines):
    # 过第一遍，拿到所有的标记行和分数
    comment_lines_score = []
    comment_lines_idx = []
    for i,line in enumerate(lines):
        if len(line)==0:
            continue
        if line[0] == "#":
            # templine = line[(line[line.find(" ")+1:]).find(" ")+1:]
            templine = line[line.find("旁"):]
            if is_chapter_name(templine) or is_scene_sep(templine):
                lines[i] = templine
                # print(templine)
            else:
                comment_lines_idx.append(i)
                comment_lines_score.append(float(line.split(" ")[1]))

    # 过第二遍，把该加的分都加上
    chaper_lines_idx = []
    for i, line in enumerate(lines):
        if is_chapter_name(line) or is_scene_sep(line):
            if i + 1 in comment_lines_idx:
                comment_lines_score[comment_lines_idx.index(i+1)] += 0.2
            # elif i - 1 in comment_lines_idx:
            #     comment_lines_score[comment_lines_idx.index(i-1)] += 0.2

    # 去掉低于0.6分的分割
    for i,line in enumerate(lines):
        if i in comment_lines_idx and comment_lines_score[comment_lines_idx.index(i)] < 0.6:
            lines[i] = line[line.find("旁"):]


    # 过第三遍，找到所有应该delete的分割
    delete_idx = []
    for i, idx in enumerate(comment_lines_idx):
        if i == 0:
            continue
        elif i > 0:
            idx_pre = comment_lines_idx[i-1]
            # 如果上一个已经被加入到即将删除的列表里面了，就不再进行判定
            if idx_pre in delete_idx:
                continue
            idx_pre += 1
            flag = 0
            # 逻辑： 始终用本分割和上一个分割进行对比
            # 情况1：如果此分割和上一个分割只隔了6个或个以下，就删掉分低的那一个。
            # 情况2：如果此分割和上一个分割全是旁白或者是只有一个人，就删掉分低的那一个
            # 情况1 情况2 依顺序依次判断，情况一满足不再进行情况二的判定
            if idx - idx_pre < 6 and comment_lines_score[i-1] < comment_lines_score[i]:
                delete_idx.append(comment_lines_idx[i-1])
                flag = 1
            elif idx - idx_pre < 6 and comment_lines_score[i-1] > comment_lines_score[i]:
                delete_idx.append(comment_lines_idx[i])
                flag = 1
            if flag == 0:
                nameset = set()
                while idx_pre < idx:
                    if lines[idx_pre].split("::")[0] != "旁白": # TODO 全旁白或者只有一个人
                        nameset.add(lines[idx_pre].split("::")[0])
                    idx_pre += 1
                if len(nameset) < 2:
                    if comment_lines_score[i-1] < comment_lines_score[i]:
                        delete_idx.append(comment_lines_idx[i-1])
                    elif comment_lines_score[i-1] > comment_lines_score[i]:
                        delete_idx.append(comment_lines_idx[i])

    # 正式进行删除
    newline = []
    newlines_with_comment= []
    for i, line in enumerate(lines):
        if i in delete_idx:
            linex = line[line.find("旁"):]
            newline.append(linex) # TODO 不应该直接删
        else:
            newline.append(line)


    return newline

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="The file to be processed")
    args = parser.parse_args()
    filelist = os.listdir(args.input_dir)

    for name in filelist:
        if name == ".txt":
            continue
        print(name)
        file_input_name = os.path.join(args.input_dir,name)
        file_outpout_name = "/nas/jiangdanyang/data/huameng_convert/"+ name + "_out.txt"
        file_input  = codecs.open(file_input_name, mode='r', encoding='utf-8')


        # if not os.path.exists("/nas/jiangdanyang/data/huameng_with_number/"+ name):
        #     continue
        # file_with_comment = codecs.open("/nas/jiangdanyang/data/huameng_with_number/"+ name, mode='r',encoding='utf-8')
        # lines_with_comment = [line.split(" ")[-1] for line in file_with_comment]

        lines = [line.strip() for line in file_input]
        # lines = [line[:line.rfind(" ")] for line in lines]
        #
        # if(len(lines) != len(lines_with_comment)):
        #     print(name+"~~~~~~~~",len(lines),len(lines_with_comment),len(file_with_comment.readlines()))
        #     continue

        newlines = processf(lines)
        # file_out1 = codecs.open("/nas/jiangdanyang/scene_cut_datas_convert/"+name+str(0),mode='w', encoding='utf-8')
        # for line in newlines:
        #     file_out1.write(line)
        #     file_out1.write('\n')
        # file_out1.close()
        err = 0
        flag  = 1
        while( flag != 0):
            flag = 0
            origin = newlines.copy()
            newlines = processf(newlines)
            for i,line in enumerate(origin):
                if line != newlines[i]:
                    flag = 1
                    # file_out1 = codecs.open("/nas/jiangdanyang/scene_cut_datas_convert/"+name+str(err+1),mode='w', encoding='utf-8')
                    # for line in newlines:
                    #     file_out1.write(line)
                    #     file_out1.write('\n')
                    # file_out1.close()
                    break
            print(name, err)
            err += 1
        # 写文件阶段
        file_output = codecs.open(file_outpout_name, mode="w", encoding='utf-8')
        # assert len(newlines)==len(lines_with_comment)
        for i, line in enumerate(newlines):
            file_output.write(line)
            # if is_number(lines_with_comment[i].strip()):
            #     file_output.write(line+" "+lines_with_comment[i].strip())
            # else:
            #     file_output.write(line+" "+"0")
            file_output.write('\n')
        file_output.close()
