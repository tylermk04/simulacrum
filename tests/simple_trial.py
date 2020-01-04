from simulacrum.api import *

import pandas as pd

class MockDatabase(SourceDatabase):
  @classmethod
  def get_rows(cls):
    return [
      {
        "patient_id": i, 
        "date_of_birth": datetime.date(1970, i, i*2)
      } for i in range(1, 13)
    ]


def my_custom_select():
  df = pd.DataFrame(MockDatabase.get_rows())
  df = df.loc[df['date_of_birth'] < datetime.date(1970, 6, 1)]
  return df 

sqlite = SqlitePersistence("test.db")

study = Study("my_test_study", "v1")
study.add_persistence(sqlite)
pop = study.load_population(my_custom_select)
print(len(pop))

consume = StudyConsumer("my_test_study", "v1")
consume.add_persistence(sqlite)
pop = consume.list_populations(SqlitePersistence)
assert len(pop) == 1
print(pop)