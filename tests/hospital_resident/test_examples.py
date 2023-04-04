"""A collection of example tests for HR."""

from matching.games import HospitalResident


def test_readme_example():
    """Test the example used in the repo README."""

    resident_prefs = {
        "A": ["C"],
        "S": ["C", "M"],
        "D": ["C", "M", "G"],
        "J": ["C", "G", "M"],
        "L": ["M", "C", "G"],
    }

    hospital_prefs = {
        "M": ["D", "L", "S", "J"],
        "C": ["D", "A", "S", "L", "J"],
        "G": ["D", "J", "L"],
    }

    capacities = {hosp: 2 for hosp in hospital_prefs}

    game = HospitalResident.create_from_dictionaries(
        resident_prefs, hospital_prefs, capacities
    )
    (A, S, D, J, L), (M, C, G) = game.residents, game.hospitals

    matching = game.solve()
    assert matching == {M: [L, S], C: [D, A], G: [J]}


def test_example_in_issue():
    """Test the example given in #67."""

    group_prefs = {
        "Group 1": ["Intellectual property", "Privacy"],
        "Group 2": ["Privacy", "Fairness in AI"],
        "Group 3": ["Privacy", "Social media"],
    }

    topic_hospital_prefs = {
        "Fairness in AI": ["Group 2"],
        "Intellectual property": ["Group 1"],
        "Privacy": ["Group 3", "Group 2", "Group 1"],
        "Social media": ["Group 3"],
    }

    capacities = {t: 2 for t in topic_hospital_prefs}

    game = HospitalResident.create_from_dictionaries(
        group_prefs, topic_hospital_prefs, capacities
    )
    (G1, G2, G3), (F, I, P, S) = game.residents, game.hospitals

    matching = game.solve()
    assert matching == {I: [G1], P: [G3, G2], F: [], S: []}


def test_resident_loses_all_preferences():
    """Test example that forces a resident to be removed."""

    resident_prefs = {"A": ["X"], "B": ["X", "Y"]}
    hospital_prefs = {"X": ["B", "A"], "Y": ["B"]}
    capacities = {"X": 1, "Y": 1}

    game = HospitalResident.create_from_dictionaries(
        resident_prefs, hospital_prefs, capacities
    )
    (_, B), (X, Y) = game.residents, game.hospitals

    matching = game.solve()
    assert matching == {X: [B], Y: []}
