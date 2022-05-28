from numpy import ndarray
import pandas as pd
from typing import List, Union


class LoadData:

    def __init__(self,
                 path: str,
                 indices_to_remove: List[int] = None,
                 headers: bool = True,
                 delete_points: bool = False,
                 sheet_name=0
                 ):
        """
        sheet_namestr: int, list, or None, default 0
        Strings are used for sheet names. Integers are used in zero-indexed sheet positions (chart sheets do not count as a sheet position). Lists of strings/integers are used to request multiple sheets. Specify None to get all worksheets.

        Available cases:

        * Defaults to 0: 1st sheet as a DataFrame

        * 1: 2nd sheet as a DataFrame

        * "Sheet1": Load sheet with name “Sheet1”

        * [0, 1, "Sheet5"]: Load first, second and sheet named “Sheet5” as a dict of DataFrame

        * None: All worksheets.
        """

        self.path = path

        # Transform input to a form which pandas accepts
        if headers:  # This only handles the case where the headers row is the first one
            self.headers = 0
        else:
            self.headers = None

        if delete_points:
            if isinstance(indices_to_remove, list):
                self.points_to_remove = indices_to_remove
            else:
                raise TypeError(f'If delete_points is True you must provide a list of points to remove. {type(indices_to_remove)} type was provided.')
        else:
            self.points_to_remove = None

        if self.path.endswith('.csv'):
            self.data = pd.read_csv(self.path, header=self.headers, skiprows=self.points_to_remove).to_numpy()
        elif self.path.endswith(('xlsx', 'xls', 'xlsm', 'xlsb', 'odf', 'ods', 'odt')):
            self.data = pd.read_excel(self.path, sheet_name=sheet_name, header=self.headers, skiprows=self.points_to_remove).to_numpy()
        else:
            raise TypeError('File type not supported yet.')
