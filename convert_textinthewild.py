"""

Convert AIHub OCR format data (only 'textinthewild') to training-datasets-splitter format data.

## References

1. AIHub OCR Data: https://aihub.or.kr/aidata/133
2. training-datasets-splitter: https://github.com/DaveLogs/training-datasets-splitter

## Usage example:
    python3 convert_textinthewild.py \
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
    │   #   [id]_[sub-id].[ext]
    │   ├── 0000000001_01.png
    │   ├── 0000000001_02.png
    │   ├── 0000000002_01.png
    │   ├── 0000000003_01.png
    │   ├── ...
    │   └── labels.txt
    │
    ├── /group2
    └── ...

* Label file structure:

    # {filename}\t{label}\n
      0000000001_01.png	abcd
      0000000001_02.png	efgh
      0000000002_01.png	ijkl
      0000000003_01.png	mnop
      ...

"""

import os
import sys
import time
import json
import argparse

from PIL import Image


def run(args):
    """ Convert AIHub OCR format data (only 'textinthewild') to training-datasets-splitter format data """

    if not os.path.exists(args.input_path):
        sys.exit(f"Can't find '{os.path.abspath(args.input_path)}' directory.")

    if not os.path.exists(args.label_file):
        sys.exit(f"Can't find '{os.path.abspath(args.label_file)}' label file.")

    # groups, count = get_files(args.input_path, except_file=args.label_file)
    groups, count = get_groups(args.input_path)

    # classes of AIHub data
    classes = ['syllable', 'word', 'sentence']

    if os.path.isdir(args.output_path):
        sys.exit(f"'{os.path.abspath(args.output_path)}' directory is already exists.")
    else:
        output_dirs = create_working_directory(args.output_path, groups, classes)

    # load label file
    create_time = time.time()
    with open(args.label_file) as f:
        json_data = json.load(f)
        label_dicts = create_label_dicts(json_data, classes, args.output_path)
    create_time = time.time() - create_time
    print("creation time of label dictionary: ", create_time)

    for ii, group in enumerate(groups):
        print("\n[%d/%d] group: '%s'" % (ii + 1, len(groups), group))
        print("-" * 40)

        start_time = time.time()

        syllable = open(os.path.join(output_dirs[group][0], "labels.txt"), "w", encoding="utf8")
        word = open(os.path.join(output_dirs[group][1], "labels.txt"), "w", encoding="utf8")
        sentence = open(os.path.join(output_dirs[group][2], "labels.txt"), "w", encoding="utf8")

        group_path = os.path.join(args.input_path, group)
        files, count = get_files(group_path)
        files.sort()

        digits = len(str(count))
        for jj, file in enumerate(files):
            if (jj + 1) % 100 == 0:
                print(("\r%{}d / %{}d Processing !!".format(digits, digits)) % (jj + 1, count), end="")

            # labels = get_labels(label_dicts, "0358769E50273F93AE951E8AA52F4F22.jpg")
            # print('labels: ', labels)
            # return
            labels = get_labels(label_dicts, file)
            for kk, label in enumerate(labels):
                # 0: class, 1: label, 2: bbox // bbox = [x, y, width, height]
                if label[0] == "character":  # syllable
                    label_file = syllable
                    output_path = output_dirs[group][0]
                elif label[0] == "word":  # word
                    label_file = word
                    output_path = output_dirs[group][1]
                elif label[0] == "sentence":  # sentence
                    label_file = sentence
                    output_path = output_dirs[group][2]
                else:
                    sys.exit(f"'{label[0]}' is not valid class type.")

                # print("label: ", label)
                # print("output_path: ", output_path)

                output_file = f"{file.split('.')[0]}_{kk:03d}.{file.split('.')[-1]}"
                with Image.open(os.path.join(group_path, file)) as img:
                    bbox = [label[2][0], label[2][1], label[2][0] + label[2][2], label[2][1] + label[2][3]]
                    if bbox[0] >= img.size[0] or bbox[1] >= img.size[1] or bbox[2] >= img.size[0] or bbox[3] >= img.size[1]:
                        print(f"{output_file} {label[0]} label's bbox error: {bbox}")
                        continue

                    # print(f"file:'{output_file}', size: '{img.size}', label:'{label[1]}', bbox:'{bbox}'")

                    crop_img = img.crop(bbox)
                    crop_img.save(os.path.join(output_path, output_file))

                label_file.write("{}\t{}\n".format(output_file, label[1]))

        elapsed_time = (time.time() - start_time) / 60.
        print("\n- processing time: %.1fmin" % elapsed_time)


def create_label_dicts(labels, classes, log_path):
    """ Create label dictionary from labels JSON data """
    dicts = {}  # key: file_name, value: values [0: class, 1: label, 2: bbox // bbox = [x, y, width, height]]

    start_idx = 0
    next_start_idx = 0
    end_idx = len(labels["annotations"])

    error_count = 0
    f = open(os.path.join(log_path, "errors.txt"), "w", encoding="utf8")

    for jdx, image in enumerate(labels["images"]):
        found_data = False
        values = []

        # skip invalid file
        invalid_files = ["0358769E50273F93AE951E8AA52F4F22.jpg"]
        if image["file_name"] in invalid_files:
            continue

        for idx in range(start_idx, end_idx):
            if labels["annotations"][idx]["image_id"] == image["id"] and labels["annotations"][idx]["text"]:

                attribute_class = labels["annotations"][idx]["attributes"]["class"]
                text = labels["annotations"][idx]["text"]
                bbox = labels["annotations"][idx]["bbox"]

                flag, msg = is_valid_label(classes, attribute_class, text, bbox, image["width"], image["height"])
                if flag is False:
                    error_count += 1
                    # print(f"[{error_count:5d}] '{image['file_name']}': {msg}")
                    f.write(f"[{error_count:5d}] '{image['file_name']}': {msg}\n")
                    continue

                # 0: class, 1: label, 2: bbox // bbox = [x, y, width, height]
                value = [labels["annotations"][idx]["attributes"]["class"],
                         labels["annotations"][idx]["text"],
                         labels["annotations"][idx]["bbox"]]
                values.append(value)
                # print('value: ', value)

                next_start_idx = idx
                found_data = True
                continue

            if found_data:
                dicts[image["file_name"]] = values
                start_idx = next_start_idx + 1
                break

    f.close()
    return dicts


def is_valid_label(classes, attribute_class, text, bbox, image_width, image_height):
    attribute_classes = classes + ["character"]

    if attribute_class not in attribute_classes:
        msg = f"'{attribute_class}' is invalid class"
        return False, msg
    elif text is None or text == "":
        msg = f"Text(label) is none"
        return False, msg
    elif bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] <= 0 or bbox[3] <= 0 \
            or bbox[0] >= image_width or bbox[1] >= image_height \
            or bbox[0] + bbox[2] >= image_width or bbox[1] + bbox[3] >= image_height:
        msg = f"'{bbox}' is invalid bbox info"
        return False, msg

    return True, None


def get_labels(dicts, file):
    """ Search label data ('class', 'text' and 'bbox') in JSON data """

    labels = []

    if file not in dicts.keys():
        print(f"\nCan't find '{file}' data in label dictionary.")
        return labels

    if len(dicts[file]) == 0:
        print(f"\n'{file}'s data is none.")
        return labels

    for value in dicts[file]:
        labels.append(value)

    return labels


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


def create_working_directory(root, sub_dirs, classes):
    sub_dirs_list = {}

    os.makedirs(root)
    for sub in sub_dirs:
        dir_list = []
        for text_class in classes:
            sub_ext = f'{sub}_{text_class}'
            path = os.path.join(root, sub_ext)
            dir_list.append(path)
            os.makedirs(path)

        sub_dirs_list[sub] = dir_list

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
