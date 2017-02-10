# US TV Schedules

## Prerequisites

- Python 2.7
- Additional Python packages (see [requirements.txt](requirements.txt))

## Installation

We recommend that you install Python virtual environment:

```
https://github.com/soodoku/tv_schedules.git
cd tv_schedules
virtualenv venv
. venv/bin/activate
```

Install Python requirements:

```
cd scripts
pip install -r requirements.txt
```

## Scraping All US TV Schedules

### Usage

```
usage: tv_schedules.py [-h] -o OUT

US TV Schedule scraper

optional arguments:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  Output filename
```

### Example

```
python tv_schedules.py -o ../data/us_tv_schedules.csv
```

## Scraping Metadata from program links (`meta_link`)

### Usage

```
usage: tv_schedules_meta.py [-h] -o OUT input

US TV Schedule metadata scraper

positional arguments:
  input              US TV Schedule data with meta link

optional arguments:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  Output filename
```

### Example

```
python tv_schedules_meta.py -o ../data/us_tv_schedules_meta.csv ../data/us_tv_schedules.csv
```

## Parse Names and Roles Data And Add Race and Gender via Python

### Usage

```
usage: names_role.py [-h] -o OUT [-s SUBSTITUTE] input

US TV Schedule name parser

positional arguments:
  input                 US TV Schedule with metadata

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     Output filename
  -s SUBSTITUTE, --substitute SUBSTITUTE
                        Subtitute list (regular expression)
```

### Example

```
python names_role.py -s us_tv_names_sub.csv -o ../data/us_tv_schedules_names.csv ../data/us_tv_schedules_meta.csv
```

### Substitions list file

There are to columns in the CSV substitution list, first column is the regular expression to be matched in the name field and another column is the substitution string.

### Export CSV name file

```
name,field,index,gender,race
```

- ``name``      Name of the person
- ``field``     Role on the TV program
- ``index``		Index number in the input
- ``gender``    Gender of the name from demographics dataset
- ``race``      Race of the name from demographics dataset

## Race and Gender of Different Roles Over Time

```
usage: race_gender_over_time.py [-h] -m META [-g GENDER] [-r RACE] -o OUT
                                input

US TV Schedule name proportion

positional arguments:
  input                 US TV Schedule name with gender and race

optional arguments:
  -h, --help            show this help message and exit
  -m META, --meta META  US TV Schedule data with meta data
  -g GENDER, --gender GENDER
                        Gender column name (default='gender')
  -r RACE, --race RACE  Race column name (default='race')
  -o OUT, --out OUT     Output filename
```

### Example

```
python race_gender_over_time.py ..\data\tv_names_race_gender.csv -o ..\data\us_tv_schedules_prop_R.csv -m ..\data\us_tv_schedules_meta.csv -g proportion_female -r cs2000_pctblack
```

The valid value of gender column can be the string of 'male'/'female' or the proportion of female in float between 0 - 1.0 or the percent of female between 0 - 100.

Similar to the gender, the race column can be the string of 'black'/'white' or the proportion of black in float between 0 - 1.0 or the percent of black between 0 - 100.

### Proportion calculation result

Create a new CSV that uses data from the names file and the show file with the
following fields:
```
for each year (aggregate over each year):
 year, 
 prop1_female_producers (proportion of shows with at least one female producer = 
 total number of shows with at least one female producer/total number of shows), 
 prop1_female_directors (proportion of shows with at least one female director), 
 prop1_female_creators (proportion of shows with at least one female creator), 
 prop_female_producers (total number of female producers divided by total number of producers), 
 prop_female_directors (total number of female directors divided by total number of directors), 
 prop_female_creators (total number of female creators divided by total number of creators), 
 prop_female_cast (total number of female cast members/total number of cast members),
 prop_female_presenters (total number of female presenters divided by total number of presenters), 
 prop1_black_producers,
 ....
```
