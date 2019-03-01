""" The Student Allocation Problem solver and core algorithm. """

from matching import Game, Matching

from .util import delete_pair, match_pair, unmatch_pair


class StudentAllocation(Game):
    """ A class for solving instances of the Student Allocation problem (SA)
    using an adapted Gale-Shapley algorithm. """

    def __init__(self, students, projects, lecturers):

        for student in students:
            student.matching = None
        for player in projects + lecturers:
            player.matching = []

        self.students = students
        self.projects = projects
        self.lecturers = lecturers

        super().__init__()
