# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import glob
import json
import os

import numpy as np
import paddle


def main(args):
    checkpoints = []
    val_scores = []

    if args.val_best:
        jsons = glob.glob(f'{args.ckpt_dir}/[!train]*.json')
        for y in jsons:
            dic_json = json.load(y)
            loss = dic_json['valid_loss']
            epoch = dic_json['epoch']
            if epoch >= args.min_epoch and epoch <= args.max_epoch:
                val_scores.append((epoch, loss))

        val_scores = np.array(val_scores)
        sort_idx = np.argsort(val_scores[:, 1])
        sorted_val_scores = val_scores[sort_idx]
        path_list = [
            args.ckpt_dir + '/{}.pdparams'.format(int(epoch))
            for epoch in sorted_val_scores[:args.num, 0]
        ]
        print("best val scores = " + str(sorted_val_scores[:args.num, 1]))
        print("selected epochs = " + str(sorted_val_scores[:args.num, 0].astype(
            np.int64)))
    else:
        path_list = glob.glob(f'{args.ckpt_dir}/[!avg][!final]*.pdparams')
        path_list = sorted(path_list, key=os.path.getmtime)
        path_list = path_list[-args.num:]

    print(path_list)

    avg = None
    num = args.num
    assert num == len(path_list)
    for path in path_list:
        print(f'Processing {path}')
        states = paddle.load(path)
        if avg is None:
            avg = states
        else:
            for k in avg.keys():
                avg[k] += states[k]
    # average
    for k in avg.keys():
        if avg[k] is not None:
            avg[k] = paddle.divide(avg[k], num)

    paddle.save(avg, args.dst_model)
    print(f'Saving to {args.dst_model}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='average model')
    parser.add_argument('--dst_model', required=True, help='averaged model')
    parser.add_argument(
        '--ckpt_dir', required=True, help='ckpt model dir for average')
    parser.add_argument(
        '--val_best', action="store_true", help='averaged model')
    parser.add_argument(
        '--num', default=5, type=int, help='nums for averaged model')
    parser.add_argument(
        '--min_epoch',
        default=0,
        type=int,
        help='min epoch used for averaging model')
    parser.add_argument(
        '--max_epoch',
        default=65536,  # Big enough
        type=int,
        help='max epoch used for averaging model')

    args = parser.parse_args()
    print(args)

    main(args)