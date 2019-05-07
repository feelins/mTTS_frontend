#!/bin/bash

work_dir='/home/shaopf/study/mTTS_frontend'
voice_name=biaobei_test
data_dir=${work_dir}/data
voice_path=${data_dir}/${voice_name}
output_path=${voice_path}/output_align
textgrid_path=${output_path}/wav

echo ${voice_path}/example_hanlp_txt.txt ${voice_path}/example_hanlp_pos_new.txt ${voice_path}/example_hanlp_pinyin.txt ${textgrid_path}
python src/gen_label.py ${voice_path}/example_hanlp_txt.txt ${voice_path}/example_hanlp_pos_new.txt ${voice_path}/example_hanlp_pinyin.txt ${textgrid_path}

