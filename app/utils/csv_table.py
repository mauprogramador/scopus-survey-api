from os.path import join

from pandas import read_csv

from app.core.config import DIRECTORY
from app.core.interfaces import CSVData


class LoadCSVData(CSVData):
    FILENAME = 'articles.csv'

    def __init__(self) -> None:
        self.__file_path = join(DIRECTORY, self.FILENAME)

    def handle(self) -> CSVData.TableType:
        try:
            csv_file = read_csv(
                self.__file_path,
                sep=';',
                encoding='utf-8',
            )
            return csv_file.to_numpy().tolist()
        except FileNotFoundError:
            return None
