# Arff
A python 3.x Module to create arff files from pandas DataFrames


A simple library to convert a pandas DataFrame to an arff file (sparse or not)

## Dependencies:
* pandas
* numpy
* dateinfer (use the actively maintained [pydateinfer](https://github.com/wdm0006/dateinfer))

## Features:
* It supports all arff datatypes:
  - Numeric
  - String
  - Nominal
  - Date
* It can create both sparse and normal arff files
* Auto convert columns of bool type to nominal attribute of values True/False
* Easy declaration of nominal values
* Auto detect the date/time format (thanks to dateinfer <3)

## Usage:
```python
    arff = Arff(
                    <name of the relation (same as filename)>,
                    <pandas dataframe>,
                    <dict that specifies data types (eg {
                                                            "ids" : int, 
                                                            "scores":numpy.dtype("float64"),
                                                            "date" : np.dtype("datetime64[ns]")
                                                            "valid" : [True, False]
                                                        }
                                                     )>,
                    <values to count as missing info (list, eg ["null", 0])>
                )
    arff.write(<save directory>, <save it as sparse file or not (bool: True -> sparse, False -> normal)>)
```

## Future Changes:
* Even for small DataFrames (*2k rows*), making a sparse arff file takes a lot of time. It is best to make it faster some day.
