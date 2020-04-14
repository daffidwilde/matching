""" A script to generate the dummy datasets used in `main.ipynb`. """

import string
import sys

import numpy as np
import pandas as pd

MAX_STUDENTS = 100
MAX_STUDENT_CHOICES = 25
MAX_SUPERVISOR_PROJECTS = 4
MAX_CAPACITY = 8
SEED = 2019

if len(sys.argv) == 6:
    MAX_STUDENTS = int(sys.argv[1])
    MAX_STUDENT_CHOICES = int(sys.argv[2])
    MAX_SUPERVISOR_PROJECTS = int(sys.argv[3])
    MAX_CAPACITY = int(sys.argv[4])
    SEED = int(sys.argv[5])

student_names = [f"19{i:04d}" for i in range(MAX_STUDENTS)]
supervisor_names = list(string.ascii_uppercase)


def create_supervisor_to_projects_map():
    """ Create a dictionary mapping supervisor names to their projects.
    To do this, first sample the number of projects that each supervisor will
    have from the discretised triangular distribution with mode
    ``.75 * MAX_SUPERVISOR_PROJECTS``. """

    mode = MAX_SUPERVISOR_PROJECTS * 0.75

    supervisor_project_numbers = (
        np.random.triangular(
            left=1,
            mode=mode,
            right=MAX_SUPERVISOR_PROJECTS,
            size=len(supervisor_names),
        )
        .round()
        .astype(int)
    )

    supervisor_to_projects = {}
    for name, number_of_projects in zip(
        supervisor_names, supervisor_project_numbers
    ):
        supervisor_to_projects[name] = [
            name + str(i) for i in range(number_of_projects)
        ]

    return supervisor_to_projects


def create_player_to_capacity_maps(supervisor_to_projects):
    """ Create dictionaries mapping supervisor names and project codes to their
    respective capacities. """

    supervisor_to_capacity, project_to_capacity = {}, {}
    for supervisor, projects in supervisor_to_projects.items():
        supervisor_capacity = np.random.randint(1, MAX_CAPACITY + 1)
        supervisor_to_capacity[supervisor] = supervisor_capacity

        for project in projects:
            project_to_capacity[project] = np.random.randint(
                1, supervisor_capacity + 2
            )

    return supervisor_to_capacity, project_to_capacity


def get_all_projects(supervisor_to_projects):
    """ Get all of the project codes available using the supervisor to projects
    map. """

    return (
        project
        for supervisor_projects in supervisor_to_projects.values()
        for project in supervisor_projects
    )


def create_student_to_choices_map(projects):
    """ Create a dictionary mapping student names to their choices of the
    available projects. To do so, first sample the number of choices each
    student makes from the discretised right-triangular distribution with
    a maximum of ``MAX_STUDENT_CHOICES``. """

    students_number_of_choices = (
        np.random.triangular(
            left=0,
            mode=MAX_STUDENT_CHOICES,
            right=MAX_STUDENT_CHOICES,
            size=len(student_names),
        )
        .round()
        .astype(int)
    )

    student_to_choices = {}
    for name, number_of_choices in zip(
        student_names, students_number_of_choices
    ):
        student_choices = np.random.choice(projects, number_of_choices).tolist()
        student_to_choices[name] = student_choices

    return student_to_choices


def create_student_dataframe(student_to_choices):
    """ Create a dataframe detailing the students' choices and assign them each
    a rank. """

    choice_columns = list(range(MAX_STUDENT_CHOICES))
    df_students = pd.DataFrame(columns=["name"] + choice_columns)

    df_students["name"] = student_to_choices.keys()

    for i, student_choices in enumerate(student_to_choices.values()):
        df_students.iloc[i, 1 : len(student_choices) + 1] = student_choices

    student_ranks = list(df_students.index)
    np.random.shuffle(student_ranks)

    df_students["rank"] = student_ranks
    df_students = df_students[["name", "rank"] + choice_columns]

    idxs = df_students[df_students["rank"] > 50].sample(3).index
    df_students.iloc[idxs, 2:] = np.nan

    return df_students


def create_supervisor_dataframe(supervisor_to_capacity):
    """ Create a dataframe detailing the supervisors' capacities. """

    df_supervisors = pd.DataFrame.from_dict(
        supervisor_to_capacity, orient="index", columns=["capacity"]
    )

    df_supervisors = df_supervisors.reset_index()
    df_supervisors.columns = ["name", "capacity"]

    return df_supervisors


def create_project_dataframe(project_to_capacity, supervisor_to_projects):
    """ Create a dataframe detailing the projects' capacities and supervisor.
    """

    df_project_capacities = pd.DataFrame.from_dict(
        project_to_capacity, orient="index", columns=["capacity"]
    )

    project_to_supervisor = {
        p: s for s, projects in supervisor_to_projects.items() for p in projects
    }

    df_project_supervisors = pd.DataFrame.from_dict(
        project_to_supervisor, orient="index", columns=["supervisor"]
    )

    df_projects = pd.concat(
        (df_project_capacities, df_project_supervisors), axis=1, sort=True
    ).reset_index()

    df_projects.columns = ["code", "capacity", "supervisor"]

    return df_projects


def save_dataframes(student_dataframe, supervisor_dataframe, project_dataframe):
    """ Save the player dataframes. """

    for df, name in zip(
        (student_dataframe, supervisor_dataframe, project_dataframe),
        ("students", "supervisors", "projects"),
    ):
        df.to_csv(f"{name}.csv", index=False)


def main():
    """ Create the required maps to form the player dataframes, and then save
    them. """

    np.random.seed(SEED)
    print("Seed set:", SEED)

    supervisor_to_projects = create_supervisor_to_projects_map()
    (
        supervisor_to_capacity,
        project_to_capacity,
    ) = create_player_to_capacity_maps(supervisor_to_projects)
    print("Supervisor and project dictionaries created...")

    all_projects = list(get_all_projects(supervisor_to_projects))

    redacted_projects = [p for p in all_projects if p != "L1"]
    student_to_choices = create_student_to_choices_map(redacted_projects)
    print("Student choices assigned...")

    df_students = create_student_dataframe(student_to_choices)
    df_supervisors = create_supervisor_dataframe(supervisor_to_capacity)
    df_projects = create_project_dataframe(
        project_to_capacity, supervisor_to_projects
    )

    save_dataframes(df_students, df_supervisors, df_projects)
    print("Dataframes saved.")


if __name__ == "__main__":
    main()
