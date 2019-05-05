#!usr/bin/env python
# -*- coding:utf-8 _*-
""" 
@author:shaopf
@file: prepare_data_for_Montreal_Align.py 
@version:
@time: 2019/04/24 20:20:45
@email:feipengshao@163.com
@function： prepare labels and dict for Montreal Alignment, need input pinyin file
"""

import os
import logging
from mtts import puncs, _set_logger
from txt2pinyin import seprate_syllable, pinyinformat


def genDictLabWord(pinyin_file, out_lab_path, out_dict_file):
    """gen data"""
    _set_logger(os.path.dirname(out_dict_file))
    logger = logging.getLogger('mtts')
    tmp_dict_list = {}
    with open(pinyin_file) as fid:
        pinyin_lines = [x.strip() for x in fid.readlines()]
    for line in pinyin_lines:
        file_name, all_pinyin = line.split('|', 1)
        save_lab_file = os.path.join(out_lab_path, file_name + '.lab')
        logger.info('gen label form montreal-align file ' + file_name)
        out_lab_list = []

        # this replace for Paic HanLP result
        # all_pinyin = all_pinyin.replace(' #', '/ ')
        # all_pinyin = all_pinyin.replace(' *', '/ ')  # not used now
        # all_pinyin = all_pinyin.replace(' $', '/ ')
        # all_pinyin = all_pinyin.replace(' %', '/ ')
        # this replace for outside Biaobei result
        all_pinyin = all_pinyin.replace('#', '/')
        all_pinyin = all_pinyin.replace('*', '/')  # not used now
        all_pinyin = all_pinyin.replace('$', '/')
        all_pinyin = all_pinyin.replace('%', '/')
        # this replace for alignment using pre trained model
        # all_pinyin = all_pinyin.replace('#', ' ')
        # all_pinyin = all_pinyin.replace('*', ' ')  # not used now
        # all_pinyin = all_pinyin.replace('$', ' ')
        # all_pinyin = all_pinyin.replace('%', ' ')

        old_pinyins = all_pinyin.split('/')
        new_pinyins = [item for item in filter(lambda x: x.strip() not in puncs and x.strip() != '', old_pinyins)]

        # output the labels
        lab_pinyins = [item for item in map(lambda x: x.replace(' ', ''), new_pinyins)]
        out_lab_list.append(' '.join(lab_pinyins))
        with open(save_lab_file, 'w') as oid:
            for item in out_lab_list:
                oid.write(item + '\n')

        # gen dict
        for word_py in new_pinyins:
            dict_word_pinyins = []
            syllable_pinyins = word_py.split()
            syllable_pinyins = [item for item in filter(lambda x: x.strip() != '', syllable_pinyins)]
            for pinyin in syllable_pinyins:
                dict_word_pinyins.append(' '.join(list(seprate_syllable(pinyinformat(pinyin)))))
            word_py = word_py.replace(' ', '')
            if word_py not in tmp_dict_list:
                tmp_dict_list[word_py] = ' '.join(dict_word_pinyins)
    result_dict = []
    for k, v in tmp_dict_list.items():
        result_dict.append(str(k) + '\t' + str(v))
    with open(out_dict_file, 'w') as oid:
        for k, v in tmp_dict_list.items():
            oid.write(str(k) + '\t' + str(v) + '\n')


if __name__ == '__main__':
    # without argparse
    # input_pinyin_file = r'../example_file/example_hanlp_pinyin.txt'
    # output_dict_file = r'../example_file/montreal_align_dict.txt'
    # output_lab_align_path = r'../example_file/lab_align'
    # genDictLabWord(input_pinyin_file, output_lab_align_path, output_dict_file)
    # print('Done!')

    # with argparse
    import argparse

    parser = argparse.ArgumentParser(
        description="convert mandarin_txt and to label and dict for montreal-forced-alignment.")
    parser.add_argument(
        "input_pinyin_file",
        help=
        "Full path to pinyinfile which each line contain file-name and pinyins (better have segment) "
    )
    parser.add_argument(
        "output_lab_align_path",
        help=
        "Full path to a directory will contain labels for montreal-alignment, will be created if it doesn't exist"
    )
    parser.add_argument(
        "output_dict_file",
        help=
        "Full path of a dict file which save the dict file for montreal-alignment")
    args = parser.parse_args()

    os.system('mkdir -p %s' % args.output_lab_align_path)

    genDictLabWord(args.input_pinyin_file, args.output_lab_align_path, args.output_dict_file)
