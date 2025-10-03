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


def test_paper_student_optimal_example():
    """
    Verify the paper's student-optimal example in Figure 1.

    The paper can be found online at:
    https://doi.org/10.1016/j.jda.2006.03.006
    """
    student_prefs = {
        "S1": ["P1", "P7"],
        "S2": ["P1", "P2", "P3", "P4", "P5", "P6"],
        "S3": ["P2", "P1", "P4"],
        "S4": ["P2"],
        "S5": ["P1", "P2", "P3", "P4"],
        "S6": ["P2", "P3", "P4", "P5", "P6"],
        "S7": ["P5", "P3", "P8"],
    }

    supervisor_prefs = {
        "L1": ["S7", "S4", "S1", "S3", "S2", "S5", "S6"],
        "L2": ["S3", "S2", "S6", "S7", "S5"],
        "L3": ["S1", "S7"],
    }

    project_supervisors = {
        "P1": "L1",
        "P2": "L1",
        "P3": "L1",
        "P4": "L2",
        "P5": "L2",
        "P6": "L2",
        "P7": "L3",
        "P8": "L3",
    }

    project_capacities = {p: 1 for p in project_supervisors}
    project_capacities["P1"] = 2
    supervisor_capacities = {"L1": 3, "L2": 2, "L3": 2}

    game = StudentProject.from_preferences(
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    )

    assert game.solve(optimal="student") == {
        "P1": ["S1"],
        "P2": ["S4"],
        "P3": ["S7"],
        "P4": ["S3"],
        "P5": ["S2"],
        "P6": [],
        "P7": [],
        "P8": [],
    }


def test_paper_supervisor_optimal_example():
    """
    Verify the paper's supervisor-optimal example in Figure 6.

    The paper can be found online at:
    https://doi.org/10.1016/j.jda.2006.03.006
    """
    student_prefs = {
        "S1": ["P3", "P1"],
        "S2": ["P1", "P3"],
        "S3": ["P4", "P2"],
        "S4": ["P2", "P4"],
    }
    supervisor_prefs = {"L1": ["S1", "S2", "S3", "S4"], "L2": ["S2", "S1", "S4", "S3"]}
    project_supervisors = {"P1": "L1", "P2": "L1", "P3": "L2", "P4": "L2"}
    project_capacities = {p: 1 for p in project_supervisors}
    supervisor_capacities = {s: 2 for s in supervisor_prefs}

    game = StudentProject.from_preferences(
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    )

    assert game.solve(optimal="supervisor") == {
        "P1": ["S1"],
        "P2": ["S3"],
        "P3": ["S2"],
        "P4": ["S4"],
    }
