"""

Convert AIHub OCR format data to deep-text-recognition-benchmark format data.

## References

1. AIHub OCR Data: https://aihub.or.kr/aidata/133
2. deep-text-recognition-benchmark: https://github.com/clovaai/deep-text-recognition-benchmark

## Usage example:
    python3 convert.py \
            --input_path ./input \
            --output_path ./output

## Input data structure:

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

* For the 'label.json' file structure, refer to the 'https://aihub.or.kr/aidata/133'

## Output data structure:

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

* Ground truth file structure:

    # {filename}\t{label}\n
      images/image_00001.png	abcd
      images/image_00002.png	efgh
      images/image_00003.png	ijkl
      ...

"""

