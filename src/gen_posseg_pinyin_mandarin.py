#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
@author: shaopf
@file: gen_posseg_pinyin_mandarin.py 
@version: 1.0
@time: 2019/07/10 09:24:36
@email: feipengshao@163.com
@function： 利用pypinyin，jieba生成汉字普通话拼音，分词，词性文件
"""
from pypinyin import pinyin, Style
from jieba import posseg
from language_util import _PUNCS
import os
import re


def txt2result(_txt):
    """Return a list of words, segs and pinyins of txt.
    _txt: input sentence
    """
    # clean punctuations
    clean_txt = _txt
    for pu in _PUNCS:
        clean_txt = clean_txt.replace(pu, '')
    words = []
    poses = []
    pinyins = []
    result_jieba = iter(posseg.cut(clean_txt))
    for word, pos in result_jieba:
        words.append(word)
        poses.append(pos[0])
        result_pypinyin = pinyin(word, style=Style.TONE3)
        pinyins.append(' '.join([item[0] for item in result_pypinyin]))

    return words, poses, pinyins


def save_result(_results, _save_dir, _save_filename, _str):
    """Save result"""
    save_file = os.path.join(_save_dir, _save_filename + '_' + _str + '.txt')
    with open(save_file, 'w') as wid:
        wid.writelines(_results)


def gen_result(_in_file):
    """Return all results for a txt file.
    _in_file: input txt file
    """
    cur_dir = os.path.dirname(_in_file)
    cur_filename = os.path.basename(_in_file)
    cur_filename = cur_filename[:cur_filename.find('.')]
    print(_in_file)
    with open(_in_file, encoding='utf-8') as fid:
        txt_lines = [x.strip() for x in fid.readlines()]
    results_words = []
    results_poses = []
    results_pinyins = []
    for line in txt_lines:
        print('processing: ', line)
        file_name, txt = re.split(' |\||\t', line, 1)
        tmp_words, tmp_poses, tmp_pinyins = txt2result(txt)
        results_words.append(file_name + '|' + '/'.join(tmp_words) + '\n')
        results_poses.append(file_name + '|' + '/'.join(tmp_poses) + '\n')
        results_pinyins.append(file_name + '|' + '/'.join(tmp_pinyins) + '\n')
    # save
    save_result(results_poses, cur_dir, cur_filename, 'pos')
    save_result(results_words, cur_dir, cur_filename, 'seg')
    save_result(results_pinyins, cur_dir, cur_filename, 'pinyin')


if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser(
    #     description="gen pos, seg, pinyin for mandarin_txt.")
    # parser.add_argument(
    #     "txtfile",
    #     help=
    #     "Full path to txtfile which each line contain file_name and txt (seperated by | or [blank] or tab) "
    # )
    # args = parser.parse_args()
    #
    # gen_result(args.txtfile)
    ##################################################################################
    input_txt_file = r'/home/shaopf/study/mTTS_frontend/data/thchs30_250_demo/A11.txt'
    gen_result(input_txt_file)
    print('Done!')