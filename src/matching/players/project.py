""" The Project class for use in instances of SA. """

from .hospital import Hospital


class Project(Hospital):
    """ A class to represent a project in an instance of SA.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    capacity : `int`
        The maximum number of matches the project can have.

    Attributes
    ==========
    faculty : `Faculty`
        The faculty player that runs the project. Defaults to `None`.
    prefs : `list`
        A list of `Player` instances in the order of the project's faculty
        preferences.
    pref_names : `list`
        A list of the names in `prefs`. Updates with `prefs`.
    matching : `list`
        The current matches of the project. An empty list if currently
        unsubscribed.
    """

    def __init__(self, name, capacity):

        super().__init__(name, capacity)
        self.faculty = None

    def set_faculty(self, faculty):
        """ Set the project's faculty member and add the project to their list
        of active projects. """

        self.faculty = faculty
        faculty.projects.append(self)

    def match(self, other):
        """ Match the project to a student, and update the project's faculty's
        matching, too. """

        self.matching.append(other)
        self.faculty.matching.append(other)
