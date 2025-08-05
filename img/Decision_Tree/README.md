# Decision Tree visualization

The pictures contained in this folder illustrate the changes caused by some parameter adjustments in the Decision Tree (DT) model.

## Requisites

Prior to executing the [dt_visualization.py](../../dt_visualization.py) script, run the functionality up to step #4 of the [Usage section](../../README.md#usage) on README in order to generate the labeled data.

## Usage

Uncomment one of the configurations around line #80 in [dt_visualization.py](../../dt_visualization.py), then execute it to generate the DT.

## Folder structure

The first number in the subfolders represents a given dataset configuration as listed below:

- `0` = example run (baseline)
- `1` = dataset after dropping the stream related features
- `2` = dataset after dropping the stream related features and applying SMOTE
- `3`-`6` = same as `2` + manual analysis and parameter adjustment based on previous results

The second number represents a parameter configuration as listed below:

- `0` = default parameters
- `1` = custom `min_samples_leaf` and `min_samples_split`
- `2` = custom `min_samples_leaf`, `min_samples_split` and `max_depth`
