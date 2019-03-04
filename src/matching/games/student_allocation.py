""" The Student Allocation Problem solver and core algorithm. """

from matching import Game, Matching

from .util import delete_pair, match_pair


class StudentAllocation(Game):
    """ A class for solving instances of the Student Allocation problem (SA)
    using an adapted Gale-Shapley algorithm. """

    def __init__(self, students, projects, faculty):

        self.students = students
        self.projects = projects
        self.faculty = faculty

        super().__init__()
