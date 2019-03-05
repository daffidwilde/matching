""" The Faculty class for instances of SA. """

from .hospital import Hospital


class Faculty(Hospital):
    """ A class to represent a faculty member in an instance of SA.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    capacity : `int`
        The maximum number of matches the faculty member can have.

    Attributes
    ==========
    projects : `list`
        The projects that the faculty member runs. Defaults to an empty list.
    prefs : `list`
        A list of `Player` instances in the order of preference.
    pref_names : `list`
        A list of the names in `prefs`. Updates with `prefs`.
    matching : `list`
        The current matches of the faculty member. An empty list if currently
        unsubscribed, and updated through its project matching updates.
    """

    def __init__(self, name):

        super().__init__(name, capacity=None)
        self.projects = []

    def set_prefs(self, students):
        """ Set the preference of the faculty member, and pass those on to the
        projects. """

        self.prefs = students
        self.pref_names = [student.name for student in students]

        for project in self.projects:
            acceptable = [
                student for student in students if project in student.prefs
            ]
            project.set_prefs(acceptable)

    def get_undersubbed_projects(self):
        """ Get a list of all the faculty's projects that are currently
        under-subscribed. """

        return [
            project
            for project in self.projects
            if len(project.matching) < project.capacity
        ]

    def get_potential_students(self):
        """ Get a list of all those students that are currently not matched to
        but have a preference of at least one under-subscribed project offered
        by the faculty. """

        return [
            student
            for student in self.prefs
            if any(
                [
                    project in student.prefs
                    for project in self.get_undersubbed_projects()
                    if student.matching != project
                ]
            )
        ]


    def get_favourite(self):
        """ Find the faculty member's favourite student that is not currently
        matched to, but has a preference of, one of the faculty's
        under-subscribed projects. Also return the student's favourite
        under-subscribed project. """

        student = self.get_potential_students()[0]
        project = [
            project
            for project in student.prefs
            if project in self.get_undersubbed_projects()
        ][0]

        return student, project
