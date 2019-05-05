#!/bin/bash

work_dir='/home/shaopf/study/mTTS_frontend'
voice_name=biaobei_test
data_dir=${work_dir}/data
voice_path=${data_dir}/${voice_name}

mkdir -p $data_dir

python src/label_for_Montreal.py ${voice_path}/example_hanlp_pinyin.txt ${voice_path}/lab_align ${voice_path}/align_dict.txt

