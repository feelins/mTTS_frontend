#!usr/bin/env python
# -*- coding:utf-8 _*-
""" 
@author:shaopf
@file: posseg_jieba.py 
@version:
@time: 2019/05/05 14:08:40
@email:feipengshao@163.com
@function： 
"""

from jieba import posseg
import re


puncs = ['”', '。', '，', '、', '？', '：', '！', '…', '—', '）', '；', '’', '!', ',', '.', ':', ';', '“', '（', '‘', '#', '*', '$', '%', ' ']


def txt2seg(txt):
    """Return a list of words and segs of txt."""

    # If txt with prosody mark, use prosody mark,
    # else use jieba position segmetation
    tmp_txt = txt
    for pu in puncs:
        tmp_txt = tmp_txt.replace(pu, '')
    words = []
    poses = []
    tmplist = iter(posseg.cut(tmp_txt))
    for word, pos in tmplist:
        words.append(word)
        poses.append(pos[0])

    return words, poses


input_txt_file = r'/home/shaopf/study/mTTS_frontend/data/biaobei_test/example_hanlp_txt.txt'
save_pos_file = r'/home/shaopf/study/mTTS_frontend/data/biaobei_test/example_hanlp_pos.txt'
with open(input_txt_file) as fid:
    txt_lines = [x.strip() for x in fid.readlines()]
results_words = []
results_poses = []
for line in txt_lines:
    print('processing: ', line)
    file_name, txt = line.split('|')
    tmp_words, tmp_poses = txt2seg(txt)
    results_words.append(file_name + '|' + ' '.join(tmp_words))
    results_poses.append(file_name + '|' + ' '.join(tmp_poses))
with open(save_pos_file, 'w') as oid:
    for line in results_poses:
        oid.write(line + '\n')
print('Done!')
