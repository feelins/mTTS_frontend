#!usr/bin/env python
# -*- coding:utf-8 _*-

import os
import re
import logging
from pypinyin import pinyin, Style, load_phrases_dict
import textgrid as tg
from mandarin_frontend import txt2label, _txt2label

consonant = [
    'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'zh',
    'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w']

puncs = ['”', '。', '，', '、', '？', '：', '！', '…', '—', '）', '；', '’', '!', ',', '.', ':', ';', '“', '（', '‘']


def _pre_pinyin_setting():
    """ fix pinyin error???"""
    load_phrases_dict({'嗯': [['ēn']]})
    load_phrases_dict({'风云变幻': [['fēng'], ['yún'], ['bià'], ['huàn']]})
    load_phrases_dict({'不破不立': [['bù'], ['pò'], ['bù'], ['lì']]})


def _add_lab(txtlines, wav_dir_path):
    """gen label file for montreal-alignment from TXT by PyPinyin"""
    logger = logging.getLogger('mtts')
    for line in txtlines:
        numstr, txt = line.split(' ')
        txt = re.sub('#\d', '', txt)
        pinyin_list = pinyin(txt.decode("utf-8"), style=Style.TONE3)
        #pinyin_list = pinyin(txt, style=Style.TONE3)
        new_pinyin_list = []
        for item in pinyin_list:
            if not item:
                logger.warning(
                    '{file_num} do not generate right pinyin'.format(numstr))
            if not item[0][-1].isdigit():
                phone = item[0] + '5'
            else:
                phone = item[0]
            new_pinyin_list.append(phone)
        lab_file = os.path.join(wav_dir_path, numstr + '.lab')
        logger.info('create lab file %s' % (lab_file))
        with open(lab_file, 'w') as oid:
            oid.write(' '.join(new_pinyin_list))

def _gen_lab(pinyin_file, wav_dir_path):
    """gen label file for montreal-alignment from TXT by PyPinyin"""
    logger = logging.getLogger('mtts')
    for line in txtlines:
        numstr, txt = line.split(' ')
        txt = re.sub('#\d', '', txt)
        pinyin_list = pinyin(txt.decode("utf-8"), style=Style.TONE3)
        # pinyin_list = pinyin(txt, style=Style.TONE3)
        new_pinyin_list = []
        for item in pinyin_list:
            if not item:
                logger.warning(
                    '{file_num} do not generate right pinyin'.format(numstr))
            if not item[0][-1].isdigit():
                phone = item[0] + '5'
            else:
                phone = item[0]
            new_pinyin_list.append(phone)
        lab_file = os.path.join(wav_dir_path, numstr + '.lab')
        logger.info('create lab file %s' % (lab_file))
        with open(lab_file, 'w') as oid:
            oid.write(' '.join(new_pinyin_list))


def _add_pinyin(txtlines, output_path):
    """txt2pinyin in one file"""
    logger = logging.getLogger('mtts')
    all_pinyin = []
    for line in txtlines:
        numstr, txt = line.split(' ')
        txt = re.sub('#\d', '', txt)
        pinyin_list = pinyin(txt, style=Style.TONE3)
        new_pinyin_list = []
        for item in pinyin_list:
            if not item:
                logger.warning(
                    '{file_num} do not generate right pinyin'.format(numstr))
            if not item[0][-1].isdigit():
                phone = item[0] + '5'
            else:
                #phone = item[0]
                phone = item[0].replace('v', 'u')
            new_pinyin_list.append(phone)
        all_pinyin.append(numstr + ' ' + ' '.join(new_pinyin_list))
    all_pinyin_file = os.path.join(output_path, 'all_pinyin.lab')
    with open(all_pinyin_file, 'w') as oid:
        for item in all_pinyin:
            oid.write(item + '\n')


def _txts_preprocess(txtfile, output_path):
    """remove all the punctuations of all text lines"""
    logger = logging.getLogger('mtts')
    with open(txtfile) as fid:
        txtlines = [x.strip() for x in fid.readlines()]
    valid_txtlines = []
    # 补充标点符号

    error_list = []  # line which contain number or alphabet
    for line in txtlines:
        num, txt = line.split(' ', 1)
        if bool(re.search('[A-Za-z]', txt)) or bool(
                re.search('(?<!#)\d', txt)):
            error_list.append(num)
        else:
            tmp_txt = txt
            for pu in puncs:
                tmp_txt = tmp_txt.replace(pu, '')
            # 去除除了韵律标注'#'之外的所有非中文文本, 数字, 英文字符符号
            if tmp_txt:
                valid_txtlines.append(num + ' ' + tmp_txt)
                logger.info('txt_processing file %s' % (num))
            else:
                logger.warning('txt error, check your txt %s' % (num))
    if error_list:
        for item in error_list:
            logger.warning(
                'Line %s contain number and alphabet! Skip this txt' % item)

    return valid_txtlines


def _txt_preprocess(txtline):
    """remove all the punctuations of one text line"""
    logger = logging.getLogger('mtts')
    valid_txtline = ''
    # 补充标点符号
    error_list = []  # line which contain number or alphabet
    if bool(re.search('[A-Za-z]', txtline)) or bool(
            re.search('(?<!#)\d', txtline)):
        error_list.append(txtline)
    else:
        tmp_txt = txtline
        for pu in puncs:
            tmp_txt = tmp_txt.replace(pu, '')
        # 去除除了韵律标注'#'之外的所有非中文文本, 数字, 英文字符符号
        if tmp_txt:
            valid_txtline = tmp_txt
            logger.info('txt_processing file %s' % (txtline))
        else:
            logger.warning('txt error, check your txt %s' % (txtline))

    if error_list:
        for item in error_list:
            logger.warning(
                'Line %s contain number and alphabet! Skip this txt' % item)
    return valid_txtline


def _standard_sfs(csv_list):
    """Change csv_list like "0 0.21 sil phones" to standard format like "2100000 s" """

    def change2absd(phone, csv_list):
        if phone in consonant:
            return 'a'
        elif phone == 'sil' or phone == 'sp':
            if float(csv_list[1]) - float(csv_list[0]) > 0.1:
                return 's'
            else:
                #return 'd'
                return 's'
        else:  #phone is vowel
            return 'b'

    standard_sfs_list = list((str(int(float(csv_list[1]) * 10e6)),
                              change2absd(csv_list[2], csv_list)))
    return standard_sfs_list


def _mfa_align(txtlines, wav_dir_path, output_path, acoustic_model_path):
    """montreal forced alignment"""
    logger = logging.getLogger('mtts')
    logger.info('Start montreal forced align')
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.makedirs('%s/wav' % output_path)
    wav_dir_real_path = os.path.realpath(wav_dir_path)
    symbolic_path = '%s/wav/mandarin_voice' % output_path
    if not os.path.exists(symbolic_path):
        os.system('ln -s %s %s' % (wav_dir_real_path, symbolic_path))
    mfa_align_path = '/home/shaopf/study/montreal-forced-aligner/montreal-forced-aligner_linux/montreal-forced-aligner/bin/mfa_align'
    lexicon_path = os.path.join(base_dir, 'misc/mandarin_mtts.lexicon')
    acoustic_model_path = os.path.join(base_dir, acoustic_model_path)

    exec_result = os.system('%s %s/wav %s %s %s/textgrid' %
              (mfa_align_path, output_path, lexicon_path, acoustic_model_path,
               output_path))
    if exec_result:
        raise OSError('Failed to run forced align tools, check if you install'
                      'montreal-forced-aligner correctly')


def _textgrid2sfs(txtlines, output_path):
    """original function"""
    logger = logging.getLogger('mtts')
    textgrid_path = os.path.join(output_path, 'textgrid/mandarin_voice')
    sfs_path = os.path.join(output_path, 'sfs')
    csv_path = os.path.join(output_path, 'csv')
    os.system('mkdir -p %s' % sfs_path)
    os.system('mkdir -p %s' % csv_path)

    for line in txtlines:
        numstr, txt = line.split(' ', 1)
        textgrid_file = os.path.join(textgrid_path, numstr + '.TextGrid')
        csv_file = os.path.join(csv_path, numstr + '.csv')
        sfs_file = os.path.join(sfs_path, numstr + '.sfs')

        if os.path.exists(textgrid_file):
            logger.info('textgrid2sfs processing file %s' % (textgrid_file))
            # textgrid to csv
            tgrid = tg.read_textgrid(textgrid_file)
            tg.write_csv(tgrid, csv_file, sep=' ', header=False, meta=False)

            # csv to sfs
            total_list = []
            with open(csv_file) as fid:
                for line in fid.readlines():
                    #start, end, name, label = line.strip().split(' ')
                    csv_list = line.strip().split(' ')
                    if csv_list[3] == 'phones':
                        total_list.append(_standard_sfs(csv_list))
            with open(sfs_file, 'w') as fid:
                for item in total_list:
                    fid.write(' '.join(item) + '\n')
        else:
            logger.warning('--Miss: %s' % textgrid_file)
            with open(os.path.join(output_path, 'error.log'), 'a+') as fid:
                fid.write('--Miss: %s \n' % textgrid_file)


def _textgrid2sfs_(textgrid_path):
    """textgrid change to sfs file which contains time boundary and label"""
    logger = logging.getLogger('mtts')
    output_path = os.path.dirname(textgrid_path)
    sfs_path = os.path.join(output_path, 'sfs')
    csv_path = os.path.join(output_path, 'csv')
    os.system('mkdir -p %s' % sfs_path)
    os.system('mkdir -p %s' % csv_path)

    for file_name in os.listdir(textgrid_path):
        file_name = file_name.split('.')[0]
        textgrid_file = os.path.join(textgrid_path, file_name + '.TextGrid')
        csv_file = os.path.join(csv_path, file_name + '.csv')
        sfs_file = os.path.join(sfs_path, file_name + '.sfs')

        logger.info('textgrid2sfs processing file %s' % (textgrid_file))
        # textgrid to csv
        tgrid = tg.read_textgrid(textgrid_file)
        tg.write_csv(tgrid, csv_file, sep=' ', header=False, meta=False)

        # csv to sfs
        total_list = []
        with open(csv_file) as fid:
            for line in fid.readlines():
                # start, end, name, label = line.strip().split(' ')
                csv_list = line.strip().split(' ')
                if csv_list[3] == 'phones':
                    total_list.append(_standard_sfs(csv_list))
        with open(sfs_file, 'w') as fid:
            for item in total_list:
                fid.write(' '.join(item) + '\n')


def _sfs2label(txtlines, output_path):
    logger = logging.getLogger('mtts')
    sfs_path = os.path.join(output_path, 'sfs')
    label_path = os.path.join(output_path, 'labels')
    os.system('mkdir -p %s/labels' % output_path)

    sfs_list = [x.replace('.sfs', '') for x in os.listdir(sfs_path)]

    process_num = 0

    for line in txtlines:
        numstr, txt = line.split()
        if numstr in sfs_list:
            process_num += 1
            sfs_file = os.path.join(sfs_path, numstr + '.sfs')
            label_file = os.path.join(label_path, numstr + '.lab')

            try:
                label_line = txt2label(txt, sfsfile=sfs_file)
                logger.info('sfs2label processing file %s' % (sfs_file))
            except Exception:
                logger.error(
                    'Error at %s, please check your txt %s' % (numstr, txt))
            else:
                with open(label_file, 'w') as oid:
                    for item in label_line:
                        oid.write(item + '\n')


def _sfs2label_(txt_file, pos_file, pinyin_file, sfs_path, output_label_path):
    """gen label"""
    logger = logging.getLogger('mtts')
    txt_lines = {}
    with open(txt_file) as fid:
        all_txt_lines = [x.strip() for x in fid.readlines()]
        for line in all_txt_lines:
            file_name, txt = line.split('|')
            txt_lines[file_name] = txt
    pos_lines = {}
    with open(pos_file) as fid:
        all_pos_lines = [x.strip() for x in fid.readlines()]
        for line in all_pos_lines:
            file_name, txt = line.split('|')
            pos_lines[file_name] = txt
    pinyin_lines = {}
    with open(pinyin_file) as fid:
        all_pinyin_lines = [x.strip() for x in fid.readlines()]
        for line in all_pinyin_lines:
            file_name, txt = line.split('|')
            pinyin_lines[file_name] = txt

    sfs_list = [x.replace('.sfs', '') for x in os.listdir(sfs_path)]

    for file_name in sfs_list:
        try:
            sfs_file = os.path.join(sfs_path, file_name + '.sfs')
            out_label_file = os.path.join(output_label_path, file_name + '.lab')
            label_line = _txt2label(txt_lines[file_name], pos_lines[file_name], pinyin_lines[file_name], sfs_file)
            logger.info('sfs2label processing file %s' % (sfs_file))
        except Exception:
            logger.error(
                'Error at %s, please check your txt' % (file_name))
        else:
            with open(out_label_file, 'w') as oid:
                for item in label_line:
                    oid.write(item + '\n')


def _set_logger(output_path):
    formater = logging.Formatter('%(levelname)-8s: %(message)s')
    logger = logging.getLogger('mtts')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname) -8s: %(message)s'))
    console_handler.setLevel(logging.INFO)

    log_path = os.path.join(output_path, 'mtts.log')
    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s'))
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG)


def generate_label(txtfile, wav_dir_path, output_path, acoustic_model_path):
    _set_logger(output_path)
    #txtlines = _txt_preprocess(txtfile, output_path)
    #_pre_pinyin_setting()
    #_add_lab(txtlines, wav_dir_path)
    #_add_pinyin(txtlines, output_path)
    #_mfa_align(txtlines, wav_dir_path, output_path, acoustic_model_path)
    _textgrid2sfs(txtlines, output_path)
    _sfs2label(txtlines, output_path)

    logger = logging.getLogger('mtts')
    logger.info('the label files are in {}/labels'.format(output_path))
    logger.info('the error log is in {}/mtts.log'.format(output_path))


if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser(
    #     description="convert mandarin_txt and wav to label for merlin.")
    # parser.add_argument(
    #     "txtfile",
    #     help=
    #     "Full path to txtfile which each line contain num and txt (seperated by a white space) "
    # )
    # parser.add_argument(
    #     "wav_dir_path",
    #     help=
    #     "Full path to a wav directory contain wav (sampling frequency should larger than 16khz)"
    # )
    # parser.add_argument(
    #     "output_path",
    #     help=
    #     "Full path to output directory, will be created if it doesn't exist")
    # parser.add_argument(
    #     '-a',
    #     '--acoustic_model_path',
    #     type=str,
    #     default='misc/thchs30.zip',
    #     help=
    #     'Full path to acoustic model for forced aligner, default is misc/thchs30.zip'
    # )
    # args = parser.parse_args()
    #
    # os.system('mkdir -p %s' % args.output_path)
    #
    # generate_label(args.txtfile, args.wav_dir_path, args.output_path,
    #                args.acoustic_model_path)
    textgrid_path = r'/home/shaopf/study/mTTS_frontend/data/biaobei_test/output_align/wav'
    _textgrid2sfs_(textgrid_path)
    input_pinyin_file = r'../data/biaobei_test/example_hanlp_pinyin.txt'
    input_txt_file = r'../data/biaobei_test/example_hanlp_txt.txt'
    input_pos_file = r'../data/biaobei_test/example_hanlp_pos.txt'
    sfs_path = r'../data/biaobei_test/output_align/sfs'
    label_path = r'../data/biaobei_test/output_align/labels'
    _sfs2label_(input_txt_file, input_pos_file, input_pinyin_file, sfs_path, label_path)
