""" Tests for each algorithm on small example cases. """

import unittest
import numpy as np
from matching.algorithms import galeshapley, extended_galeshapley


class TestGaleShapleyAlgorithms(unittest.TestCase):
    """ Test class for standard and capacitated Gale-Shapley algorithms. """

    def test_galeshapley(self):
        """ Small, workable example for the Gale-Shapley algorithm. """

        suitor_preferences = {
            "A": ["D", "E", "F"],
            "B": ["D", "F", "E"],
            "C": ["F", "D", "E"],
        }

        reviewer_preferences = {
            "D": ["B", "C", "A"],
            "E": ["A", "C", "B"],
            "F": ["C", "B", "A"],
        }

        solution = galeshapley(suitor_preferences, reviewer_preferences)

        self.assertEqual(set(suitor_preferences.keys()), set(solution.keys()))
        self.assertEqual(
            set(np.unique([val for val in reviewer_preferences.keys()])),
            set(np.unique([val for val in solution.values()])),
        )

        expected_solution = {"A": "E", "B": "D", "C": "F"}

        self.assertEqual(expected_solution, solution)

    def test_extended_galeshapley(self):
        """ Example used on the NRMP website for the capacitated Gale-Shapley
        algorithm. Again, this example is easily solved on paper.
        """

        suitor_preferences = {
            "A": ["C"],
            "S": ["C", "M"],
            "J": ["C", "G", "M"],
            "L": ["M", "C", "G"],
            "D": ["C", "M", "G"],
        }

        reviewer_preferences = {
            "M": ["D", "J"],
            "C": ["D", "A", "S", "L", "J"],
            "G": ["D", "A", "J", "L"],
        }

        capacities = {"M": 2, "C": 2, "G": 2}

        str_matching, rvwr_matching = extended_galeshapley(
            suitor_preferences, reviewer_preferences, capacities
        )

        self.assertEqual(
            set(suitor_preferences.keys()), set(str_matching.keys())
        )
        self.assertEqual(
            set(reviewer_preferences.keys()), set(rvwr_matching.keys())
        )

        expected_str_matching = {
            "A": "C",
            "S": None,
            "J": "G",
            "L": "G",
            "D": "C",
        }

        expected_rvwr_matching = {"M": [], "C": ["D", "A"], "G": ["J", "L"]}

        self.assertEqual(str_matching, expected_str_matching)
        self.assertEqual(rvwr_matching, expected_rvwr_matching)


if __name__ == "__main__":
    unittest.main()
