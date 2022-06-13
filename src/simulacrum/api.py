import abc
import datetime
import sqlite3
from typing import Mapping, Callable, List

import pandas as pd
from sqlalchemy import Integer, ForeignKey, String, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


class Study:
  def __init__(self, name: str, version_id: str):
    self.name = name
    self.version_id = version_id
    self.__persistence: List[Persistence] = []

  def add_persistence(self, pst):
    self.__persistence.append(pst)

  def load_population(self, callable_: Callable[..., pd.DataFrame], *args, **kwargs):
    ret = callable_(*args, **kwargs)
    self.__persist(f"{self.name}__population__{self.version_id}", ret)
    return ret

  def __persist(self, ident: str, df: pd.DataFrame):
    for ps in self.__persistence:
      ps.store_table(ident, df)


class Predicate(abc.ABC):
  @abc.abstractmethod
  def include(self, row) -> bool:
    pass


class Population:
  def __init__(self, members: dict):
    self.members = members


class Cohort:
  def __init__(self):
    self.members = {}


class StudyMatrix:
  def __init__(self, matrix):
    self.matrix = matrix


class Persistence:
  """Interface for data storage
  """
  pass

  __population_table_name = "pop_"

  @abc.abstractmethod
  def store_table(self, ident, tbl: pd.DataFrame):
    pass


class SqlitePersistence(Persistence):
  def __init__(self, path, add_index=False, overwrite_mode="replace"):
    self.path = path
    self.__add_index=add_index
    self.__overwrite_mode=overwrite_mode

  def __repr__(self):
    return f'<sqlite {self.path}>'

  def __connect(self):
    return sqlite3.connect(self.path)

  def store_table(self, ident, tbl: pd.DataFrame):
    tbl.to_sql(ident, self.__connect(), index=self.__add_index, if_exists=self.__overwrite_mode)

  def list_populations(self):
    return self.__connect().cursor().execute(
      "SELECT tbl_name FROM sqlite_master WHERE tbl_name like '%population%'"
    ).fetchall()


class SourceDatabase(abc.ABC):
  @abc.abstractclassmethod
  def get_rows(cls) -> list:
    pass


class StudyConsumer:
  def __init__(self, study_name, study_version):
    self.name = study_name
    self.study_verison = study_version
    self.__persistence = []

  def add_persistence(self, pst):
    self.__persistence.append(pst)

  def list_populations(self, pst_class):
    return {
      pst.__repr__(): pst.list_populations()
      for pst in list(filter(lambda p: p.__class__ == pst_class, self.__persistence))
    }
    
