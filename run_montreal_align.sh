#!/bin/bash

work_dir='/home/shaopf/study/mTTS_frontend'
voice_name=biaobei_test
data_dir=${work_dir}/data
voice_path=${data_dir}/${voice_name}
out_path=${voice_path}/output_align
mfa_path='/home/shaopf/study/montreal-forced-aligner/montreal-forced-aligner_linux/montreal-forced-aligner/bin/'

mkdir -p $out_path

# use pre trained model
use_pre_trained_model=false


if [ "$use_pre_trained_model" = true ]; then
    # Using pre trained acoustic model...
    model_path='/home/shaopf/study/mTTS_frontend/misc/thchs30.zip'
    model_lexicon_path='misc/mandarin_mtts.lexicon'
    ${mfa_path}/mfa_align ${voice_path}/wav ${model_lexicon_path} ${model_path} ${out_path}
else
    # Train acoustic model and align...
    model_lexicon_path=${voice_path}/align_dict.txt
    ${mfa_path}/mfa_train_and_align ${voice_path}/wav ${model_lexicon_path} ${out_path}/TextGrid
fi