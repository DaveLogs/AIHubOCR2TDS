# AIHubOCR2TDS
Convert AIHub OCR format data to training-datasets-splitter format data.

## References

- [AIHub OCR](https://aihub.or.kr/aidata/133): Korean text images
- [training-datasets-splitter](https://github.com/DaveLogs/training-datasets-splitter): Split the training datasets into 'training'/'validation'/'test' data.

## Usage example

### Convert datasets for 'printed', 'printed_augmentation' and 'handwritten' group.
```bash
(venv) $ python3 convert.py \
                --input_path ./input \
                --label_file ./input/labels.json \
                --output_path ./output
```

### Convert datasets for 'textinthewild' group. 
```bash
(venv) $ python3 convert_textinthewild.py \
                --input_path ./input \
                --label_file ./input/labels.json \
                --output_path ./output
```


## Input Data Structures

The structure of input data folder as below.

* Input: [AIHub OCR](https://aihub.or.kr/aidata/133) format data 

```
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
```

### Label file structure

For the 'label_info.json' file structure, refer to the [AIHub OCR](https://aihub.or.kr/aidata/133). 


## Output Data Structure

The structure of output data folder as below.

* Output: for use in [training-datasets-splitter](https://github.com/DaveLogs/training-datasets-splitter) project.

```
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
```

### Label file structure

* labels.txt

```
# {filename}\t{label}\n
  0000000001.png	abcd
  0000000002.png	efgh
  0000000003.png	ijkl
  ...
```
