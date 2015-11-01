#coding:utf-8

import os
import fnmatch
import argparse
import codecs
import re

def find_targets(base_path):
    targets = []
    for root, dirnames, filenames in os.walk(base_path):
        for filename in fnmatch.filter(filenames, '*.js'):
            targets.append(os.path.join(root, filename))
    return targets

def trim_prefix(path, prefix):
    return path.replace(prefix, '')

def convert_real_path(base_path, require_path):
    # 共通するパス以降のディレクトリパスを取得する
    particular_path_nodes = []
    require_path_nodes = require_path.split('/')
    while len(require_path_nodes):
        if base_path.find('/'.join(require_path_nodes)) > -1:
            break
        particular_path_nodes.insert(0, require_path_nodes.pop())

    # 共通する部分のパスを取得する
    common_path_pos = 0
    base_path_nodes = base_path.split('/')
    while len(base_path_nodes):
        if '/'.join(base_path_nodes).endswith('/'.join(require_path_nodes)):
            break
        common_path_pos += 1
        base_path_nodes.pop()

    if common_path_pos == 0:
        converted_path = './' + '/'.join(particular_path_nodes)
    else:
        converted_path = '../' * common_path_pos + '/'.join(particular_path_nodes)

    return converted_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert path from symbolic link into real path')
    parser.add_argument('path', type=str, metavar='path', help='target source directory')
    parser.add_argument('--prefix', type=str, metavar='prefix', default='app', help='symbolic link prefix')

    args = parser.parse_args()
    base_path = args.path
    prefix = args.prefix

    print(base_path, prefix)

    # require statement match require_pattern
    require_pattern = re.compile('require\([\'"](.*)[\'"]\)')

    sources = find_targets(base_path)
    for src in sources:
        file = codecs.open(src, mode='r', encoding='utf-8')
        new_file = codecs.open(src + '.tmp', mode='w', encoding='utf-8')

        line = file.readline()
        while line:
            matched = require_pattern.search(line)
            if matched:
                require_path = matched.group(1)
                if require_path.startswith(prefix + '/'):
                    # prefix部分は実際のパスに含まれないので除去する
                    converted_path = convert_real_path(os.path.dirname(src), trim_prefix(require_path, prefix))
                    converted_line = line.replace(require_path, converted_path)
            else:
                converted_line = line

            new_file.write(converted_line)

            line = file.readline()
        file.close()
        new_file.close()

        os.rename(new_file.name, file.name)
