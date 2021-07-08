"""

Convert AIHub OCR format data to training-datasets-splitter format data.

## References

1. AIHub OCR Data: https://aihub.or.kr/aidata/133
2. training-datasets-splitter: https://github.com/DaveLogs/training-datasets-splitter

## Usage example:
    python3 convert.py \
            --input_path ./input \
            --label_file ./input/labels.json \
            --output_path ./output

## Input data structure:

    /input
    ├── label_info.json
    ├── /group1
    │   #   [id].[ext]
    │   ├── 0000000001.png
    │   ├── 0000000002.png
    │   ├── 0000000003.png
    │   └── ...
    │
    ├── /group2
    └── ...

* For the 'label_info.json' file structure, refer to the 'https://aihub.or.kr/aidata/133'

## Output data structure:

    /output
    ├── /group1
    │   #   [filename].[ext]
    │   ├── 0000000001.png
    │   ├── 0000000002.png
    │   ├── ...
    │   └── labels.txt
    │
    ├── /group2
    └── ...

* Label file structure:

    # {filename}\t{label}\n
      0000000001.png	abcd
      0000000002.png	efgh
      0000000003.png	ijkl
      ...

"""

import os
import sys
import time
import json
import bisect
import shutil
import argparse


def run(args):
    """ Convert AIHub OCR format data to training-datasets-splitter format data """

    if not os.path.exists(args.input_path):
        sys.exit(f"Can't find '{os.path.abspath(args.input_path)}' directory.")

    if not os.path.exists(args.label_file):
        sys.exit(f"Can't find '{os.path.abspath(args.label_file)}' label file.")

    # groups, count = get_files(args.input_path, except_file=args.label_file)
    groups, count = get_groups(args.input_path)

    if os.path.isdir(args.output_path):
        sys.exit(f"'{os.path.abspath(args.output_path)}' directory is already exists.")
    else:
        _ = create_working_directory(args.output_path, groups)

    # load label file
    with open(args.label_file) as f:
        labels_info = json.load(f)

    for ii, group in enumerate(groups):
        print("\n[%d/%d] group: '%s'" % (ii+1, len(groups), group))
        print("-" * 40)

        start_time = time.time()
        output_path = os.path.join(args.output_path, group)
        with open(os.path.join(output_path, "labels.txt"), "w", encoding="utf8") as f:

            group_path = os.path.join(args.input_path, group)
            files, count = get_files(group_path)
            files.sort()

            names, ids = get_name_and_ids(labels_info)

            digits = len(str(count))
            for jj, file in enumerate(files):
                if (jj + 1) % 100 == 0:
                    print(("\r%{}d / %{}d Processing !!".format(digits, digits)) % (jj + 1, count), end="")

                label = get_text(labels_info, names, ids, file)
                f.write("{}\t{}\n".format(file, label))

                fr = os.path.join(group_path, file)
                to = os.path.join(output_path, file)
                shutil.copy(fr, to)

        elapsed_time = (time.time() - start_time) / 60.
        print("\n- processing time: %.1fmin" % elapsed_time)


def get_name_and_ids(labels):
    """ Extract 'file_name' and 'image_ids' from JSON data """
    names = []
    for image in labels["images"]:
        names.append(image["file_name"])

    ids = []
    for annotation in labels["annotations"]:
        ids.append(annotation["image_id"])

    return names, ids


def get_text(labels, names, ids, file):
    """ Search text in nested JSON data """

    idx = bisect.bisect(names, file) - 1
    image_id = labels["images"][idx]["id"]

    if image_id == "":
        sys.exit(f"Can't find '{file}' data in 'images' of label file.")

    idx = bisect.bisect(ids, image_id) - 1
    text = labels["annotations"][idx]["text"]

    if text == "":
        sys.exit(f"Can't find '{image_id}' data in 'annotations' of label file.")

    return text


def get_groups(path):
    group_list = []

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            print('except file name: ', item)
            continue

        group_list.append(item)

    return group_list, len(group_list)


def get_files(path, except_file=""):
    file_list = []

    for file in os.listdir(path):
        if file.startswith(".") or file == os.path.basename(except_file):
            print('except file name: ', file)
            continue

        file_list.append(file)

    return file_list, len(file_list)


def create_working_directory(root, sub_dirs):
    sub_dirs_list = {}
    os.makedirs(root)
    for sub in sub_dirs:
        path = os.path.join(root, sub)
        sub_dirs_list[sub] = path
        os.makedirs(path)

    return sub_dirs_list


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert dataset for training-datasets-splitter')

    parser.add_argument('--label_file', type=str, required=True, help='File path of label info')
    parser.add_argument('--input_path', type=str, required=True, help='Data path of AIHub OCR format data')
    parser.add_argument('--output_path', type=str, required=True,
                        help='Data path for use in training-datasets-splitter project')

    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == '__main__':
    arguments = parse_arguments()
    run(arguments)

