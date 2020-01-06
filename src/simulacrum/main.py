from simulacrum.fake_data_helpers import random_date
from simulacrum import utils

from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import choice
from pathlib import Path


class Subject:
    """Class representing a patient/study subject.

    May or may not be useful. Present to show illustrate framework design possibilities.
    """
    pass


class Database:
    """Defines the data available (i.e. i2b2, a sql database; etc)

    Think of 'patients' and 'encounters' here as sql tables.
    """
    
    patients = [
        dict(
            id=i, 
            sex=choice(['M', 'F']),
            dob=random_date()
        ) for i in range(30)
    ]

    encounters = [
        dict(
            id=p['id'] * 3,
            patient_id=p['id'],
            date=random_date(earliest=p['dob'])
        ) for p in patients if p['id'] % 3 == 0
    ]


class Population:
    """This would define how to filter the Database to get the study population.

    i.e. "a list of patient IDs is obtained for everybody that meets the general criteria..."
    """
    
    @classmethod
    def load(cls):
        # patients with encounters
        query = [
            {
                "patient": p,
                "encounters": [e for e in Database.encounters if e['patient_id'] == p['id']]
            }
            for p in Database.patients
        ]
        return [p for p in query if p['encounters'] != []]

    @classmethod
    def load_patient_ids(cls):
        return [p['patient']['id'] for p in cls.load()]

    @classmethod
    def load_demographic_table(cls):
        ids = Population.load_patient_ids()
        demographic_table = [
            p for p in Database.patients
            if p['id'] in ids
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

    def __init__(self, name, population, eligibility, study_design):
        self.name = name # i.e. anything: Metformin Study A, Study 09024, etc
        self.population = population
        self.eligibility = eligibility
        self.study_design = study_design

    def __setup(self):
        """Sets up the storage 
        """
        outpath: Path = Path('.') / "output" / self.name
        outpath.mkdir(exist_ok=True, parents=True)
        self.outpath = outpath

    def cache(self, fn, rows):
        """Exports the intermediate files as needed.
        """
        print(f"caching {fn} table")
        fn = f"{fn}.csv"
        utils.store_table(self.outpath / fn, rows)

    def load_population(self):
        """This would load the base population ids, and join to their demographic info
        """
        return self.population.load_demographic_table()

    def load_fact_table(self):
        """This would load the full fact table, i.e. joined encounters
        """
        return self.population.load()

    def feature_engineering(self, fact_table):
        # calculate eligibility indicators, etc
        for row in fact_table:
            row['is_medicare_eligible'] = relativedelta(datetime.utcnow(), row['patient']['dob']).years > 70
        # also run nlp, etc here
        for row in fact_table:
            row['has_dementia'] = choice((True, False,))
        # output is the study matrix
        return fact_table

    def apply_eligibility(self, feature_table):
        return self.study_design.apply(
            self.eligibility.apply(
                feature_table
            )
        )

    def run(self):
        """Runs the study
        """
        self.__setup()
        pop = self.load_population()
        self.cache("demographics", pop)
        patient_facts = self.load_fact_table()
        self.cache("facts", patient_facts)
        feature_table = self.feature_engineering(patient_facts)
        self.cache("features", feature_table)
        final = self.apply_eligibility(feature_table)
        self.cache("study_matrix", final)

pop = Population()
elig = Eligibility()
design = AsTreatedStudy()

Study("my_fake_study", pop, elig, design).run()
