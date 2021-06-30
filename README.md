# AIHubOCR2DTRB
Convert AIHub OCR format data to deep-text-recognition-benchmark format data.

## Reference

- [AIHub OCR](https://aihub.or.kr/aidata/133): Korean text images
- [deep-text-recognition-benchmark](https://github.com/clovaai/deep-text-recognition-benchmark): Text recognition (optical character recognition) with deep learning methods.

## Usage example

```bash
(venv) $ python3 convert.py \
                --input_path ./input \
                --output_path ./output
```

## Input Data Structures

The structure of input data folder as below.

* Input: [AIHub OCR](https://aihub.or.kr/aidata/133) format data

```
/input
├── label.json
├── /group1
│   #   [id].[ext]
│   ├── 0001.png
│   ├── 0002.png
│   ├── 0003.png
│   └── ...
│
├── /group2
└── ...
```

### Label file structure

For the 'label.json' file structure, refer to the [AIHub OCR](https://aihub.or.kr/aidata/133). 


## Output Data Structure

The structure of output data folder as below.

* Output: for use in [deep-text-recognition-benchmark](https://github.com/clovaai/deep-text-recognition-benchmark) project.

```
/output
├── /group1
│   ├── gt.txt
│   └── /images
│       #   image_[idx].[ext]
│       ├── image_00001.png
│       ├── image_00001.png
│       ├── image_00001.png
│       └── ...
│
├── /group2
└── ...
```

### Ground truth file structure

* gt.txt

```
# {filename}\t{label}\n
  images/image_00001.png	abcd
  images/image_00002.png	efgh
  images/image_00003.png	ijkl
  ...
```
