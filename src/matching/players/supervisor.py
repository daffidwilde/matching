"""The Supervisor class for use in instances of SA."""

from .hospital import Hospital


class Supervisor(Hospital):
    """Supervisor player class for instances of SA.

    Parameters
    ----------
    name : object
        An identifier. This should be unique and descriptive.
    capacity : int
        The maximum number of matches the supervisor can have.

    Attributes
    ----------
    projects : list of Project
        The projects that the supervisor runs. Defaults to an empty
        list.
    prefs : list of Player
        The supervisor's preferences. Defaults to ``None`` and is
        updated via the ``set_prefs`` method.
    pref_names : list
        A list of the names in ``prefs``. Updates with ``prefs`` via
        ``set_prefs``.
    matching : list of Player
        The current matches of the supervisor. An empty list if
        currently unsubscribed, and updated through its projects'
        matching updates.
    """

    def __init__(self, name, capacity):
        super().__init__(name, capacity)
        self.projects = []

    def _forget(self, student):
        """Attempt to forget the student.

        A student is only removed if it is not ranked by any of the
        supervisor's projects.
        """

        if student in self.prefs and not any(
            [student in project.prefs for project in self.projects]
        ):
            prefs = self.prefs[:]
            prefs.remove(student)
            self.prefs = prefs

    def set_prefs(self, students):
        """Set the preference list for the supervisor.

        This method also passes the preferences on to its projects
        according to those students who ranked each project.
        """

        self.prefs = students
        self._pref_names = [student.name for student in students]
        self._original_prefs = students[:]

        for project in self.projects:
            acceptable = [
                student for student in students if project in student.prefs
            ]
            project.set_prefs(acceptable)

    def get_favourite(self):
        """Get the supervisor's favourite viable student.

        A student is viable if they are not currently matched to, but
        have a preference of, one of the supervisor's under-subscribed
        projects. This method also returns the student's favourite
        under-subscribed project. If no such student exists, return
        ``None``.
        """

        if len(self.matching) < self.capacity:
            for student in self.prefs:
                for project in student.prefs:
                    if (
                        project.supervisor == self
                        and student not in project.matching
                        and len(project.matching) < project.capacity
                    ):
                        return student, project

        return None
