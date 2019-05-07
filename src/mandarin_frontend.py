#!usr/bin/env python
# -*- coding:utf-8 _*-

import re
import os
from jieba import posseg
from labcnp import LabGenerator
from labformat import tree
from txt2pinyin import txt2pinyin, seprate_syllable, pinyinformat
#from mtts import puncs

puncs = ['”', '。', '，', '、', '？', '：', '！', '…', '—', '）', '；', '’', '!', ',', '.', ':', ';', '“', '（', '‘']


def _adjust(prosody_txt):
    """Make sure that segment word is smaller than prosody word
    this function happened in the background that we have manually labeled prosody,
    Does these prosodys are really bigger than segment words? means #2 bigger than #1?

    for example:
    prosody_txt: 今天的#2新#2闻#4
    seg_txt: 今天#1的#1新闻#4
    the #2 between 新 and 闻 need adjust here!!!!!

    """
    prosody_words = re.split('#\d', prosody_txt)
    rhythms = re.findall('#\d', prosody_txt)
    txt = ''.join(prosody_words)
    words = []
    poses = []
    for word, pos in posseg.cut(txt):
        words.append(word)
        poses.append(pos[0])
    index = 0
    insert_time = 0
    length = len(prosody_words[index])
    i = 0
    while i < len(words):
        done = False
        while not done:
            if (len(words[i]) > length):
                #print(words[i], prosody_words[index])
                length += len(prosody_words[index + 1])
                rhythms[index] = ''
                index += 1
            elif (len(words[i]) < length):
                # print(' less than ', words[i], prosody_words[index])
                rhythms.insert(index + insert_time, '#0')
                insert_time += 1
                length -= len(words[i])
                i += 1
            else:
                # print('equal :', words[i])
                # print(rhythms)
                done = True
                index += 1
        else:
            if (index < len(prosody_words)):
                length = len(prosody_words[index])
            i += 1
    if rhythms[-1] != '#4':
        rhythms.append('#4')
    rhythms = [x for x in rhythms if x != '']
    return (words, poses, rhythms)


def txt2label(txt, sfsfile=None, style='default'):
    '''Return a generator of HTS format label of txt.

    Args:
        txt: like raw txt "向香港特别行政区同胞澳门台湾同胞"
             or txt with prosody make like "向#1香港#2特别行政区#1同胞#3澳门台湾#1同胞",
             punctuation is also allow in txt
        sfsfile: absolute path of sfs file (alignment file). A sfs file
            example(measure time by 10e-7 second, 12345678 means 1.2345678
            second)
            --------
            239100 s
            313000 a
            323000 d
            400000 b
            480000 s
            ---------
            a stands for consonant
            b stands for vowel
            d stands for silence that is shorter than 100ms
            s stands for silence that is longer than 100ms
        style: label style, currently only support the default HTS format

    Return:
        A generator of phone label for the txt, convenient to save as a label file
    '''
    assert style == 'default', 'Currently only default style is support in txt2label'

    # delete all character which is not number && alphabet && chinese word

    # If txt with prosody mark, use prosody mark,
    # else use jieba position segmetation
    tmp_txt = txt
    for pu in puncs:
        tmp_txt = tmp_txt.replace(pu, '')
    if tmp_txt.find('#') != -1:
        words, poses, rhythms = _adjust(tmp_txt)
    else:
        txt = re.sub('[,.，。]', '#4', txt)
        words = []
        poses = []
        tmplist = iter(posseg.cut(tmp_txt))
        for word, pos in tmplist:
            words.append(word)
            poses.append(pos[0])
        rhythms = ['#0'] * (len(words) - 1)
        rhythms.append('#4')

    syllables = txt2pinyin(''.join(words))

    phone_num = 0
    for syllable in syllables:
        phone_num += len(syllable)  # syllable is like ('b', 'a3')

    if sfsfile:
        phs_type = []
        times = ['0']
        with open(sfsfile) as fid:
            for line in fid.readlines():
                line = line.strip().rstrip('\n')
                assert len(line.split(' ')) == 2, 'check format of sfs file'
                time, ph = line.split(' ')
                times.append(int(float(time)))
                phs_type.extend(ph)
    else:
        phs_type = []
        for i, rhythm in enumerate(rhythms):
            single_word_pinyin = txt2pinyin(words[i])
            single_word_phone_num = sum(
                [len(syllable) for syllable in single_word_pinyin])
            phs_type.extend(['a'] * single_word_phone_num)
            if i != (len(rhythms) - 1) and rhythm == '#4':
                phs_type.append('s')
        '''
        phs_type = ['a'] * phone_num
        '''
        phs_type.insert(0, 's')
        phs_type.append('s')
        times = [0] * (len(phs_type) + 1)
    '''
    for item in words:
        print(item)

    print ('words: ', words)
    print ('rhythms: ',rhythms)
    print ('syllables: ', syllables)
    print ('poses: ', poses)
    print ('phs_type: ', phs_type)
    print ('times: ', times)
    '''

    phone = tree(words, rhythms, syllables, poses, phs_type)
    return LabGenerator(phone, rhythms, times)


def _txt2label(txt, pos_txt, pinyin_txt, sfsfile=None, style='default'):
    """Return a generator of HTS format label of txt.
    change by shaopf: not use jieba this time, because there is already prosody here.

    Args:
        txt: like raw txt "0001|向#1香港#2特别行政区#1同胞#3澳门台湾#1同胞"
             punctuation is allow in txt
        pos_txt: like raw txt "0001|n n n n n n"
             it has to have the same list order and number with word txt.
        pinyin_txt: like raw txt " 0001|xiang4 xiang1 gang3 te4 bie2..."
            it has to have the same list order and number with word txt.
        sfsfile: absolute path of sfs file (alignment file). A sfs file
            example(measure time by 10e-7 second, 12345678 means 1.2345678
            second)
            --------
            239100 s
            313000 a
            323000 d
            400000 b
            480000 s
            ---------
            a stands for consonant
            b stands for vowel
            d stands for silence that is shorter than 100ms
            s stands for silence that is longer than 100ms
        style: label style, currently only support the default HTS format

    Return:
        A generator of phone label for the txt, convenient to save as a label file
    """
    assert style == 'default', 'Currently only default style is support in txt2label'

    # delete all character which is not number && alphabet && chinese word

    # If txt with prosody mark, use prosody mark,
    # else use jieba position segmetation
    tmp_txt = txt
    for pu in puncs:
        tmp_txt = tmp_txt.replace(pu, '')
    if tmp_txt.find('#') != -1:
        words = re.split('#\d', tmp_txt)
        words = [item for item in filter(lambda x: x.strip() != '', words)]
        rhythms = re.findall('#\d', tmp_txt)
        poses = pos_txt.split(' ')
        #words, poses, rhythms = _adjust_(tmp_txt, pos_txt)
    else:
        txt = re.sub('[,.，。]', '#4', txt)
        words = []
        poses = []
        tmplist = iter(posseg.cut(tmp_txt))
        for word, pos in tmplist:
            words.append(word)
            poses.append(pos[0])
        rhythms = ['#0'] * (len(words) - 1)
        rhythms.append('#4')

    syllables = []
    pinyin_list = pinyin_txt.split(' ')
    for item in pinyin_list:
        syllables.append(seprate_syllable(pinyinformat(item)))

    phone_num = 0
    for syllable in syllables:
        phone_num += len(syllable)  # syllable is like ('b', 'a3')

    if sfsfile:
        phs_type = []
        times = ['0']
        with open(sfsfile) as fid:
            for line in fid.readlines():
                line = line.strip().rstrip('\n')
                assert len(line.split(' ')) == 2, 'check format of sfs file'
                time, ph = line.split(' ')
                times.append(int(float(time)))
                phs_type.extend(ph)
    else:
        phs_type = []
        for i, rhythm in enumerate(rhythms):
            single_word_pinyin = txt2pinyin(words[i])
            single_word_phone_num = sum(
                [len(syllable) for syllable in single_word_pinyin])
            phs_type.extend(['a'] * single_word_phone_num)
            if i != (len(rhythms) - 1) and rhythm == '#4':
                phs_type.append('s')
        '''
        phs_type = ['a'] * phone_num
        '''
        phs_type.insert(0, 's')
        phs_type.append('s')
        times = [0] * (len(phs_type) + 1)
    '''
    for item in words:
        print(item)

    print ('words: ', words)
    print ('rhythms: ',rhythms)
    print ('syllables: ', syllables)
    print ('poses: ', poses)
    print ('phs_type: ', phs_type)
    print ('times: ', times)
    '''

    phone = tree(words, rhythms, syllables, poses, phs_type)
    return LabGenerator(phone, rhythms, times)


if __name__ == '__main__':
    txt = '绿#1是#0阳春#1烟景#3大块#1文章的#1底色四月的#1林峦#3更是#0绿得#1鲜活#1秀媚#1诗意盎然#4'
    pos_txt = 'n n n n n n n n n n n n n'
    pinyin_txt = 'lv4 shi4 yang2 chun1 yan1 jing3 da4 kuai4 wen2 zhang1 de5 di3 se4 si4 yue4 de5 lin2 luan2 geng4 shi4 lv4 de2 xian1 huo2 xiu4 mei4 shi1 yi4 ang4 ran2'
    sfsfile = r'/home/shaopf/study/mTTS_frontend/data/thchs30_250_demo/output/sfs/A11_0.sfs'
    for i in list(_txt2label(txt, pos_txt, pinyin_txt, sfsfile)):
        print(i)
    # txt = '绿是阳春烟景大块文章的底色四月的林峦更是绿得鲜活秀媚诗意盎然'
    # for i in list(txt2label(txt)):
    #     print(i)
    """
    import argparse
    parser = argparse.ArgumentParser(description="convert mandarin_txt to label for merlin.")
    parser.add_argument("txtfile",
                        help="Full path to txtfile which each line contain num and txt (seperated by a white space) ")
    parser.add_argument("output_path",
                        help="Full path to output directory, will be created if it doesn't exist")
    parser.add_argument("-s", "--sfs_dir_path", type=str, default=None,
                        help="Full path to sfs directory, won't generate time stamp if it is None")

    args = parser.parse_args()

    os.system('mkdir -p %s' % args.output_path)
    txtlines = _txt_preprocess(args.txtfile, args.output_path)

    for line in txtlines:
        print('processing: ',line)
        numstr, txt = line.split(' ',1)
        '''
        if args.sfs_dir_path:
            sfs_file = os.path.join(args.sfs_dir_path, numstr+'.sfs')
            labresult = txt2label(txt, sfsfile=sfs_file)
        else:
            labresult = txt2label(txt)
        '''
        try:
            if args.sfs_dir_path:
                sfs_file = os.path.join(args.sfs_dir_path, numstr+'.sfs')
                labresult = txt2label(txt, sfsfile=sfs_file)
            else:
                labresult = txt2label(txt)
        except Exception:
            print('Error at %s, please check your txt or sfs file %s' % (numstr, txt))
        else:
            with open(os.path.join(args.output_path, numstr+'.lab'), 'w') as fid:
                    for lab in labresult:
                        fid.write(lab+'\n')
    """
