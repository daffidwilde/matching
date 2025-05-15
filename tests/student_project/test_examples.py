"""A collection of example tests for SA."""

from matching.games import StudentProject


def test_example_in_docs():
    """Verify the example used in the discussion page of SA."""

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

    game = StudentProject.from_preferences(
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    )

    matching = game.solve()
    assert matching == {"X1": ["A", "C"], "X2": [], "Y1": ["D"], "Y2": ["B", "E"]}
