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

    def __init__(self, name, capacity):

        super().__init__(name, capacity)
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

    def forget(self, student):
        """ Only forget a student if it is not ranked by any of the faculty's
        projects. """

        if not any([student in project.prefs for project in self.projects]):
            prefs = self.prefs[:]
            prefs.remove(student)
            self.prefs = prefs

    def get_favourite(self):
        """ Find the faculty member's favourite student that it is not currently
        matched to, but has a preference of, one of the faculty's
        under-subscribed projects. Also return the student's favourite
        under-subscribed project. """

        if len(self.matching) < self.capacity:
            for student in self.prefs:
                for project in student.prefs:
                    if (
                        project.faculty == self
                        and student not in project.matching
                        and len(project.matching) < project.capacity
                    ):
                        return student, project

        return None
