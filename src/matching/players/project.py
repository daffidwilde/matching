""" The Project class for use in instances of SA. """

from .hospital import Hospital


class Project(Hospital):
    """ A class to represent a project in an instance of SA.

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
    prefs : list of Player
        The project's preferences. Inherited from ``supervisor``.
    pref_names : list
        A list of the names in ``prefs``. Updates with ``prefs`` via the
        ``supervisor.set_prefs`` method.
    matching : list of Player
        The current matches of the project. An empty list if currently
        unsubscribed.
    """

    def __init__(self, name, capacity):

        super().__init__(name, capacity)
        self.supervisor = None

    def set_supervisor(self, supervisor):
        """ Set the project's supervisor and add the project to their list
        of active projects. """

        self.supervisor = supervisor
        if self not in supervisor.projects:
            supervisor.projects.append(self)

    def match(self, student):
        """ Match the project to ``student``, and update the project
        supervisor's matching to include ``student``, too. """

        self.matching.append(student)
        self.matching.sort(key=self.prefs.index)
        self.supervisor.match(student)

    def unmatch(self, student):
        """ Break the matching between the project and ``student``, and the
        matching between ``student`` and the project supervisor. """

        matching = self.matching[:]
        matching.remove(student)
        self.matching = matching
        self.supervisor.unmatch(student)

    def forget(self, student):
        """ Remove ``student`` from the preference list of the project and its
        supervisor. """

        if student in self.prefs:
            prefs = self.prefs[:]
            prefs.remove(student)
            self.prefs = prefs
            self.supervisor.forget(student)
