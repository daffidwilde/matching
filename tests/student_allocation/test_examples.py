""" A collection of example tests. """

from matching.games import StudentAllocation, student_allocation


def test_example_in_docs():
    """ Verify the example used in the discussion page of SA. """

    student_prefs = {
        "A": ["X1", "X2"],
        "B": ["Y2", "X2", "Y1"],
        "C": ["X1", "Y1", "X2"],
        "D": ["Y2", "X1", "Y1"],
        "E": ["X1", "Y2", "X2", "Y1"],
    }

    supervisor_prefs = {
        "X": ["B", "C", "A", "E", "D"],
        "Y": ["B", "C", "E", "D"],
    }

    project_supervisors = {"X1": "X", "X2": "X", "Y1": "Y", "Y2": "Y"}
    project_capacities = {p: 2 for p in project_supervisors}
    supervisor_capacities = {sup: 3 for sup in supervisor_prefs}

    game = StudentAllocation.create_from_dictionaries(
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    )
    a, b, c, d, e = game.students
    (x1, x2, y1, y2), (x, y) = game.projects, game.supervisors

    matching = student_allocation(
        game.students, game.projects, game.supervisors
    )
    assert matching == {x1: [c, a], x2: [], y1: [d], y2: [b, e]}
