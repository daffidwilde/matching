"""The Project class for use in instances of SA."""

from .hospital import Hospital


class Project(Hospital):
    """Project player class for instances of SA.

    Parameters
    ----------
    name : object
        An identifier. This should be unique and descriptive.
    capacity : int
        The maximum number of matches the project can have.

    Attributes
    ----------
    supervisor : Supervisor
        The supervisor that runs the project. Defaults to ``None``.
        Controlled using the ``set_supervisor`` method.
    prefs : list of Player
        The project's preferences. Inherited from ``supervisor`` and set
        via the ``Supervisor.set_prefs`` method.
    matching : list of Player
        The current matches of the project. An empty list if currently
        unsubscribed.
    """

    def __init__(self, name, capacity):
        super().__init__(name, capacity)
        self.supervisor = None

    def _forget(self, student):
        """Remove a student from the project preference list.

        This method also prompts the supervisor to attempt forgetting
        the student.
        """

        if student in self.prefs:
            prefs = self.prefs[:]
            prefs.remove(student)
            self.prefs = prefs
            self.supervisor._forget(student)

    def _match(self, student):
        """Match the project to the student.

        This method also updates the project supervisor's matching to
        include the student.
        """

        self.matching.append(student)
        self.matching.sort(key=self.prefs.index)
        self.supervisor._match(student)

    def _unmatch(self, student):
        """Break the matching between the project and the student.

        This method also breaks the matching between the student and the
        project supervisor.
        """

        matching = self.matching[:]
        matching.remove(student)
        self.matching = matching
        self.supervisor._unmatch(student)

    def set_supervisor(self, supervisor):
        """Assign the supervisor to the project.

        This method also update the supervisor's project list.
        """

        self.supervisor = supervisor
        if self not in supervisor.projects:
            supervisor.projects.append(self)
