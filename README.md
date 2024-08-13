# Time-Step Classification Benchmarking Datasets

This repo contains files related to the datasets used for benchmarking models under the **Time Step Classification** category on Ready tensor. There are 5 benchmarking datasets used in this category. Additionally, a sixth dataset called `multi_frequency_sinusoidal` is used for smoke testing (i.e. sanity checks) of models. The list of datasets is as follows:

| dataset                    | # of samples | # classes | # features | min series length | max series length | time frequency | source link                                                                         |
| -------------------------- | :----------: | :-------: | :--------: | :---------------: | :---------------: | :------------: | ----------------------------------------------------------------------------------- |
| eeg_eye_state              |      1       |     2     |     14     |       14980       |       14980       |     OTHER      | [link](https://archive.ics.uci.edu/dataset/264/eeg+eye+state)                       |
| har70plus                  |      18      |     7     |     6      |        871        |       1536        |     OTHER      | [link](https://archive.ics.uci.edu/dataset/780/har70)                               |
| hmm_continuous             |     500      |     4     |     3      |        50         |        300        |     OTHER      | synthetic                                                                           |
| multi_frequency_sinusoidal |     100      |     5     |     2      |        109        |        499        |     OTHER      | synthetic                                                                           |
| occupancy_detection        |      1       |     2     |     5      |       20560       |       20560       |    SECONDLY    | [link](https://archive.ics.uci.edu/dataset/357/occupancy+detection)                 |
| pamap2                     |      9       |    12     |     31     |        64         |       2725        |     OTHER      | [link](https://archive.ics.uci.edu/dataset/231/pamap2+physical+activity+monitoring) |

All datasets are already processed and can be found in the `datasets/processed` folder.

The HAR70 dataset is an aggregated version of the [HAR dataset](https://archive.ics.uci.edu/dataset/780/har) from the UCI Machine Learning Repository. Data were mean aggregated over 100 time steps to create a dataset with fewer time steps.

## Repository Structure

The `./datasets` folder contains the main data files and the schema files for all the benchmark datasets.

- `processed` folder contains the processed files. These files are used in the Ready Tensor platform for model benchmarking.
  - The CSV file with suffix `_train.csv` is used for training. This file excludes the forecast horizon. The forecast horizon is the time period for which the model is expected to generate forecasts. This file contains columns for the series id, time, and the target value. It may also contain columns for past and future covariates.
  - The CSV file with suffix `_test.csv` is used for input to the forecast step. It represents the forecast horizon for which the model is expected to generate forecasts. This file contains columns for the series id, and time. It may also contain columns for future covariates. The target value is not included in this file.
  - `_test_key.csv` contains the data for the forecast horizon. This test key file is used to generate scores by comparing with forecasts. This file contains columns for the series id, time, and the target value.
  - The JSON file with suffix `_schema.json` is the schema file for the corresponding dataset.
  - The CSV file with the dataset name, and no other suffix, is the full data made of both training data, and data from the forecast horizon.
- The `raw` folder contains the original data files from the source and the Jupyter Notebooks used to generate the processed files.
- The `./src/generate_schemas.py` script is used to generate the JSON schema files for all datasets. This script uses the two CSV configuration files in the `src/config` folder.

---

## License

The code in this repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

The datasets included in this repository are provided for convenience and are subject to their respective licenses as provided by the original authors and distributors. For more details on the licenses and to access the original datasets, please refer to the original sources as mentioned in the dataset descriptions above.

Please ensure compliance with the respective licenses when using these datasets.
