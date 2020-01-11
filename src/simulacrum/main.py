from simulacrum.fake_data_helpers import random_date
from simulacrum import utils
from simulacrum.i2b2 import i2b2, query

from collections import namedtuple
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import choice
from pathlib import Path


class Subject(namedtuple('Subject', ['patient', 'encounters', 'features'], defaults=[dict()])):
    """Class representing a patient/study subject.

    May or may not be useful. Present to show illustrate framework design possibilities.
    """
    pass

class Database:
    """Defines the data available (i.e. i2b2, a sql database; etc)

    Think of 'patients' and 'encounters' here as sql tables.
    """
    
    patients = query(i2b2.patient_dimension)

    encounters = query(i2b2.observation_fact)

class Population:
    """This would define how to filter the Database to get the study population.

    i.e. "a list of patient IDs is obtained for everybody that meets the general criteria..."
    """

    def load(self):
        # patients with encounters
        query = [
            Subject(
                p,
                [e for e in Database.encounters if e.patient_num == p.patient_num]
            )
            for p in Database.patients
        ]
        return [p for p in query if p.encounters != []]

    def load_patient_ids(self):
        return set(subject.patient.patient_num for subject in self.load())

    def load_demographic_table(self):
        ids = self.load_patient_ids()
        demographic_table = [
            p for p in Database.patients
            if p.patient_num in ids
        ]
        return demographic_table


class Encounter:
    """Based on my understanding of i2b2, a patient can have 
    multiple encounters (one-to-many relationship). I presume the "fact table"
    query conducts a "flattening" of encounters into features/columns.

    But it may be wortwhile to treat patients -> encounter(s) as an object graph
    for the purposes of computation (instead of a flat table)
    """
    pass


class Matrix:
    """The final output of the study
    
    i.e. "filter down to the final patients and covariates..."

    this is exported for "statistical analysis and plotting"
    """
    pass


class Eligibility:
    """Placeholder to show how domain elements can be represented as classes.

    See `Study.apply_eligibility` for usage
    """

    __author = "John Smith, PhD"
    __last_updated = "2019-12-30"
    __version = "v3"

    def apply(self, table):
        """filters the table based on eligibility criteria"""
        # i.e. if row['is_dead'] drop row
        return table


class StudyDesign:
    """Placeholder to show how domain elements can be represented as classes.
     
    See `Study.apply_eligibility` for usage
    """
    def apply(self, table):
        """applies the study design to a subject table.
        """
        return table


class IntentionToTreatStudy(StudyDesign):
    """This is where you'd define the manipulation for intention to treat
    """
    pass


class AsTreatedStudy(StudyDesign):
    """As treated definition
    """
    pass


class Study:
    """The study itself, which is the logical ordering of population query, 
    feature engineering and eligibility/study design application to produce the final
    "study matrix" (can't remember if that is the correct term, please correct my terminology as needed).
    """

    def __init__(self, name, population: Population, eligibility, study_design):
        self.name = name # i.e. anything: Metformin Study A, Study 09024, etc
        self.__hashed_name = "abc9234fas90dfh"
        self.population = population
        self.eligibility = eligibility
        self.study_design = study_design

    def __setup(self):
        """Sets up the storage 
        """
        outpath: Path = Path('.') / "output" / self.name
        outpath.mkdir(exist_ok=True, parents=True)
        self.outpath = outpath

    def load_from_cache(self, step_name, step_version=None):
        if step_version is None:
            step_version = "latest_version"
        q = self.database.query(
            f"""
            select * 
            from step_name_{step_version}
            """
        )
        return q

    def save_output(self, step_name, rows):
        """Exports the intermediate files as needed.
        """
        print(f"saving {step_name} table")
        step_name = f"{step_name}.csv"
        return
        utils.store_table(self.outpath / step_name, rows)
        utils.save_step_run_metadata(step_name)

    def load_population(self):
        """This would load the base population ids, and join to their demographic info
        """
        self.next = self.load_fact_table
        return self.population.load_demographic_table()

    def load_fact_table(self):
        """This would load the full fact table, i.e. joined encounters
        """
        self.next = self.feature_engineering
        self._fact_table = self.population.load()
        return self._fact_table

    def feature_engineering(self):
        fact_table = self._fact_table
        # calculate eligibility indicators, etc
        for row in fact_table:
            row.features['ckd'] = relativedelta(datetime.utcnow(), row.patient.birth_date).years > 71
        # also run nlp, etc here
        for row in fact_table:
            row.features['has_dementia'] = choice((True, False,))
        # output is the study matrix
        self._feature_table = fact_table
        self.next = self.apply_eligibility
        return fact_table

    def apply_eligibility(self):
        self.next = None
        return self.study_design.apply(
            self.eligibility.apply(
                self._feature_table
            )
        )

    @property
    def _steps(self):
        return {
            "demographics": self.load_population,
            "facts": self.load_fact_table,
            "features": self.feature_engineering,
            "study_matrix": self.apply_eligibility,
        }

    def run(self, start_at=None, end_after=None):
        """Runs the study
        """
        self.__setup()
        if start_at:
            start_at = self._steps.get(start_at)
            start_at()
        else:
            list(self._steps.values())[0]()
        while self.next is not None:
            self.next()

pop = Population()
elig = Eligibility()
design = AsTreatedStudy()

my_study = Study("my_metformin_study", pop, elig, design)
my_study.run()

# my_study.run(end_after="facts")

# my_study.run(start_at="features")
