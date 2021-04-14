#! /usr/bin/env bash

CUDA_VISIBLE_DEVICES=0 \
python3 -u ${BIN_DIR}/train.py \
--device 'gpu' \
--nproc 1 \
--config conf/conformer.yaml \
--output ckpt

if [ $? -ne 0 ]; then
    echo "Failed in training!"
    exit 1
fi


exit 0