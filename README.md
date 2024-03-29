# DPLocate Modules

There are five DPLocate modules. They are run in tandem. Their dependencies are:

* MATLAB >= 2017a
* https://www.mathworks.com/products/mapping.html
* Python >= 3.6
* pandas

# Installation

* Make sure you have the stated MATLAB and Python
* Install the [Mapping Toolbox](https://www.mathworks.com/products/mapping.html)

  The toolbox should automatically install when you install MATLAB.
  Otherwise, [this](https://www.mathworks.com/matlabcentral/answers/1457044-install-a-toolbox-from-command-line?s_tid=mlc_ans_email_ques)
  thread may be helpful to install it later. You can verify its existence by running
  [this](https://www.mathworks.com/help/map/creating-maps-using-geoshow.html) quick example.


* Install Python packages:

      pip install -r requirements.txt

* Finally, clone this repository:

      git clone https://github.com/dptools/dplocate.git
    
  Individual module scripts are `dplocate/dplocate*/*py`. Learn more about them below.
  

# DPLocate0-read
DPLocate Step 0: Extract the raw GPS data

## Table of contents
1. [Requirements](#requirements)
2. [Usage](#usage)

## Requirements
- The Raw data is saved as an unencrypted `.json` file that is saved in 
the 'phone/gps/raw' directory 

- The Data has the following format:

```text
{"sensor": "lamp.gps", "data": {"latitude": (deg), "longitude": (deg), 
"accuracy": m, "altitude": (deg)}, "timestamp": (JAVA time)}
```

- The output directory can be edited. The default is `./processed/gps_dash2` and the 
  file is saved as `file_gps.mat` which contains five vector variables in MATLAB
  with the following names and contents:

```text
t1:   timestamp(JAVA time)
lat1: latitude(deg)
lon1: longitude(deg)
alt1: altitude(deg)
acc1: accuracy(m)
```

- This step is the longest part of the pipeline and it can take hours per 
  subject. Running that in parallel for different subjects of a study is 
  recommended to reduce the execution time.

- After this step run dplocate-preprocess pipeline


### Passphrase
(Encryption is not applied currently so you can skip all the *Passphrase* sections)

For files that are locked, please provide a passphrase by setting the 
`BEIWE_STUDY_PASSCODE` environment variable.
For example:
```
export BEIWE_STUDY_PASSCODE='test passcode 1 2 3'
```

## Usage
The default is that the pipeline runs for the `new` files.

```bash
# To generate reports for subject A and subject C in STUDY_PILOT under their processed folders
# Define the PHOENIX, consent and MATLAB directories 
parse_gps_mc.py --phoenix-dir [PHOENIX DIR] --consent-dir [CONSENT DIR] --matlab-dir [MATLAB DIR] --study STUDY_PILOT --data-type phone --include active --data-dir PROTECTED --subject A C

```

For more information, please run

```bash
parse_gps_mc.py -h
```

# DPLocate1-preprocess
DPLocate Step 1: Preprocess the GPS data with temporal filtering

## Table of contents
1. [Requirements](#requirements)
2. [Usage](#usage)

## Requirements
- The Input to this module is the Output of dplocate0-read. The input data is saved as an unencrypted
  `file_gps.mat` file.
 
- The Data has the following format:
    - Five vector variables in MATLAB with the following names and contents:

```text
t1:   timestamp(JAVA time)
lat1: latitude(deg)
lon1: longitude(deg)
alt1: altitude(deg)
acc1: accuracy(m)
```

- The output directory can be edited. The default is `./processed/gps_dash2` and the 
  file is saved as `dash.mat`.
  
- This step applies temporal filtering by defining 'epochs' 
  and saves the summary of the epochs; as the following columns:
  
  ![image](https://user-images.githubusercontent.com/69796473/124317866-d81df380-db45-11eb-9db0-262e0a6e4044.png)

- After this step run dplocate2-process pipeline


### Passphrase
For files that are locked, please provide a passphrase by setting the 
`BEIWE_STUDY_PASSCODE` environment variable.
For example:
```
export BEIWE_STUDY_PASSCODE='test passcode 1 2 3'
```

## Usage
The default is that the pipeline runs for the `new` files.

```bash
# To generate reports for subject A and subject C in STUDY_PILOT under their processed folders
# Define the PHOENIX, consent and MATLAB directories 
preprocess_gps_mc.py --phoenix-dir [PHOENIX DIR] --consent-dir [CONSENT DIR] --matlab-dir [MATLAB DIR] --study STUDY_PILOT --data-type phone --include active --data-dir PROTECTED --subject A C

```

For more information, please run
```bash
preprocess_gps_mc.py -h
```

# DPLocate2-process
DPLocate Step 2: Process the GPS data with clustering (every 150 days for long studies)

## Table of contents
1. [Requirements](#requirements)
2. [Usage](#usage)

## Requirements
- The Input to this module is the Output of dplocate1-preprocess. 
  The input data is saved as an unencrypted `dash.mat` file.

- The Data has the following format:
    - Epoch data from row 1 with the following columns:
![image](https://user-images.githubusercontent.com/69796473/124317501-46ae8180-db45-11eb-8b34-07f408fc09df.png)

- The output directory can be edited. The default is `./processed/gps_dash2` and the 
  file is saved as `daily_nr#.mat` where # is a natural number from 1 to inf.

- This step applies spatial clustering to the 'epochs' and saves the daily maps and the 
  coordinates of the Points of Interest (PoIs).
- After this step run dplocate3-aggregate pipeline


### Passphrase
For files that are locked, please provide a passphrase by setting the 
`BEIWE_STUDY_PASSCODE` environment variable.
For example:
```
export BEIWE_STUDY_PASSCODE='test passcode 1 2 3'
```

## Usage
```bash
# To generate reports for subject A and subject C in STUDY_PILOT under their processed folders
# Define the PHOENIX, consent and MATLAB directories 
process_gps_mc.py --phoenix-dir [PHOENIX DIR] --consent-dir [CONSENT DIR] --matlab-dir [MATLAB DIR] --study STUDY_PILOT --data-type phone --include active --data-dir PROTECTED --subject A C

```

For more information, please run
```bash
process_gps_mc.py -h
```
# DPLocate3-aggregate
DPLocate Step 3: Aggregate the processed daily maps of the study

## Table of contents
1. [Requirements](#requirements)
2. [Usage](#usage)

## Requirements
- The Input to this module is the Output of dplocate2-process. 
  The input data is saved as encrypted `daily_nr#.mat` files.

- The output directory can be edited. The default is `./processed/gps_dash2` and the 
  file is saved as `daily_all.mat`.

- This step aggregates the daily maps of the 150-day clusters.

- After this step run dplocate4-plot pipeline


### Passphrase
For files that are locked, please provide a passphrase by setting the 
`BEIWE_STUDY_PASSCODE` environment variable.
For example:
```
export BEIWE_STUDY_PASSCODE='test passcode 1 2 3'
```

## Usage
```bash
# To generate reports for subject A and subject C in STUDY_PILOT under their processed folders
# Define the PHOENIX, consent and MATLAB directories 
aggregate_gps_mc.py --phoenix-dir [PHOENIX DIR] --consent-dir [CONSENT DIR] --matlab-dir [MATLAB DIR] --study STUDY_PILOT --data-type phone --include active --data-dir PROTECTED --subject A C
```

For more information, please run
```bash
aggregate_gps_mc.py -h
```

# DPLocate4-plot
DPLocate Step 4: Plot color-coded GPS daily map

## Table of contents
1. [Requirements](#requirements)
2. [Usage](#usage)

## Requirements
- The Input to this module is the Output of dplocate3-aggregate. 
  The input data is saved as encrypted `daily_all.mat` files.

- The output directory can be edited. The default is GENERAL directory `/phone/processed/mtl_plt` and the 
  file is saved as `STUDY_SUBJECT-tmzn.png.`.

- This step plots the daily maps and transfers the processed data into the GENERAL folder.


### Passphrase
For files that are locked, please provide a passphrase by setting the 
`BEIWE_STUDY_PASSCODE` environment variable.
For example:
```
export BEIWE_STUDY_PASSCODE='test passcode 1 2 3'
```

## Usage

```bash
# To generate reports for subject A and subject C in STUDY_PILOT under their processed folders
# Define the PHOENIX, consent and MATLAB directories 
phone_gps_mc.py --phoenix-dir [PHOENIX DIR] --consent-dir [CONSENT DIR] --matlab-dir [MATLAB DIR] --study STUDY_PILOT --data-type phone --include active --data-dir PROTECTED --subject A C
```

For more information, please run
```bash
phone_gps_mc.py -h
```
