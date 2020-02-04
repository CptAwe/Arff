__author__ = "GeoPap"
"""
A simple library to convert a pandas DataFrame to an arff file (sparse or not)

Features:
    - It supports all arff datatypes:
        > Numeric
        > String
        > Nominal
        > Dates
    - It can create both sparse and normal arff files
    - Auto convert columns of bool type to nominal attribute of values True/False
    - Easy declaration of nominal values
    - Auto detect the date/time format (thanks to dateinfer <3)

Usage:
    arff = Arff(
                    <name of the relation (same as filename)>,
                    <pandas dataframe>,
                    <dict that specifies data types (eg {
                                                            "ids" : int, 
                                                            "scores":numpy.dtype("float64"),
                                                            "date" : np.dtype("datetime64[ns]"),
                                                            "valid" : [True, False],
                                                            "num" : [1, 2, 3] 
                                                        }
                                                     )>,
                    <values to count as missing info (list, eg ["null", 0])>
                )
    arff.write(<save directory>, <save it as sparse file or not (bool: True -> sparse, False -> normal)>)
"""

import pandas as pd
import numpy as np
import dateinfer


def getdateformat(dates: list):
    dates = list(dates.astype(str))
    date_format = dateinfer.infer(dates)
    return date_format


class Arff:

    def __init__(self, name: str, data: pd.DataFrame, specific_formats: dict, extra_missing: list):

        # General Info
        __relation = "@RELATION "
        self._attribute = "@ATTRIBUTE "
        self._data = "@DATA"
        self._missingvalue = "?"

        # Extra info
        self._extra_missing = extra_missing

        # Sparse related info
        self._sparsevalue = [0, 0.0]
        self._sparseright = "}"
        self._sparceleft = "{"
        self._dummyname = "dummy"
        self._dummytype = "STRING"
        self._dummyvalue = "dummy"



        self._attr_types = {
            "number": {
                "title": "NUMERIC",
                "left": "",
                "right": ""
            },
            "string": {
                "title": "STRING",
                "left": "",
                "right": ""
            },
            "nominal": {
                "title": "",
                "left": "{",
                "right": "}"
            },
            "date": {
                "title": "DATE ",
                "left": "[",
                "right": "]"
            }
        }

        self._content_str = []
        self._relation = __relation + name
        self._content_df = data
        self._Attributes = list(data.columns)
        self.__createAttributes(specific_formats)

    def __addnewline(self):
        self._content_str.append("\n")

    def __addrelation(self):
        self._content_str.append(self._relation)

    def __addattribute(self, attribute):
        self._content_str.append(attribute)

    def __adddatadeclaration(self):
        self._content_str.append(self._data)

    def __adddata(self, row: list, sparse=False):
        data = ", ".join(row)
        if sparse:
            data = self._sparceleft + data
            data = data + self._sparseright
        self._content_str.append(data)

    def __makeattributenominal(self, name, proposed_values):
        correct_values = np.unique(self._content_df[name])
        proposed_values = np.array(proposed_values)
        # Test if the two arrays have the same elements
        if (not np.isin(correct_values, proposed_values).all()) and \
                (not np.isin(proposed_values, correct_values).all()):
            raise ValueError('''Inconsistency between proposed and actual values of %s'''%(name))
        return str(list(proposed_values)).strip("[]()")

    def __createAttributes(self, specific_formats):
        # Each column name must be in a format like this:
        # for NUMERIC/STRING   : <column_name>@<datatype>
        # for NOMINAL          : <column_name>@{<the_values>}
        # for DATE             : <column_name>@{<date_format} (?)

        changed_names = []
        for col in zip(self._content_df.columns, self._content_df.dtypes):
            original_name = col[0]
            original_datatype = col[1]

            convert_to_nominal = False

            if original_name in specific_formats:
                correct_type = specific_formats[original_name]
                if type(correct_type) != type and type(correct_type) != np.dtype:
                    # A list of values is specified
                    convert_to_nominal = True
                    proposed_values = correct_type
                    types = np.array(list(map(type, correct_type)))
                    if len(np.unique(types.astype(str))) != 1:
                        raise ValueError('''\rInvalid specification for nominal values for:
                                            \r\t%s - %s
                                            \rAll values must be of equal type''' % (original_name, correct_type))
                    correct_type = types[0]

                # A type is specified
                if original_datatype != correct_type:
                    self._content_df[original_name] = self._content_df[original_name].astype(correct_type)
                original_datatype = correct_type

            name = original_name.replace(" ", "_")  # Replace any spaces in the column names with "_"
            name = name + "@"

            choose = ""
            content = ""
            if convert_to_nominal:
                choose = "nominal"
                content = self.__makeattributenominal(original_name, proposed_values)
            else:
                if original_datatype == bool:
                    choose = "nominal"
                    content = "True, False"
                elif original_datatype in (np.int64, np.float64):
                    choose = "number"
                elif original_datatype == str:
                    choose = "string"
                elif original_datatype == np.dtype("datetime64[ns]"):
                    choose = "date"
                    date_format = getdateformat(self._content_df[original_name].dropna().values)
                    self._content_df[original_name] = pd.to_datetime(self._content_df[original_name], format=date_format)
                    content = date_format
                else:
                    raise ValueError("Unspecified type %s for column %s" % (original_datatype, name))

            name = name + self._attr_types[choose]["title"] + \
                   self._attr_types[choose]["left"] + \
                   content + \
                   self._attr_types[choose]["right"]

            changed_names.append(name)

        self._content_df.columns = changed_names

    def __createarff(self):
        total_rows = len(self._content_df)
        for i in range(total_rows):
            print("\rCreating arff row %s out of %s"%(i+1, total_rows), end="")
            row = self._content_df.loc[i, :].values.astype(str)
            self.__adddata(row)
        print(end="")

    def __createsparsearff(self):
        total_rows = len(self._content_df)
        for i in range(total_rows):
            print("\rCreating sparse arff row %s out of %s"%(i+1, total_rows), end="")
            # Add a column in the begging to fix the problem of sparse arff files
            # see more here: https://www.cs.waikato.ac.nz/ml/weka/arff.html

            row = self._content_df.iloc[[i], :].copy()
            row.insert(loc=0, column=self._dummyname, value=self._dummyvalue)

            row_str = []
            for index, col in enumerate(row):
                try:
                    if row[col].values[0] in self._sparsevalue:
                        continue
                except Exception as e:
                    print(e)
                    raise ValueError("The above problem was encountered. Check if your attributes are unique.")
                row_str.append("%s %s" % (index, row[col].values[0]))

            # row = row.values.astype(str)[0]
            # print(row)

            self.__adddata(row_str, True)
        print(end="")

    def __fillContent(self, sparse):
        """
        fills the __content_str with the lines of the arff file
        :param: sparse:
        :return:
        """

        # Put the name of the relation
        self.__addrelation()
        self.__addnewline()

        # Create the Attributes
        if sparse:
            self.__addattribute(self._dummyname + " " + self._dummytype)

        for col in self._content_df.columns:
            name, info = col.split("@")
            self.__addattribute(name + " " + info)

        # Add the data
        self.__addnewline()
        self.__adddatadeclaration()

        # Declare missing values
        self._content_df = self._content_df.fillna(self._missingvalue)
        for val in self._extra_missing:
            self._content_df = self._content_df.replace(val, self._missingvalue)

        print("Creating arff file...")
        if sparse:
            self.__createsparsearff()
        else:
            self.__createarff()

    def write(self, save_dir_tmp, sparse=False):
        """
        Write the arff to file
        :param save_dir_tmp:
        :param sparse:
        :return:
        """

        self.__fillContent(sparse)

        with open(save_dir_tmp, 'w', encoding='utf-8') as file:
            file.write("\n".join(self._content_str))
