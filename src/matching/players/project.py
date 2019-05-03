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
    supervisor : `Supervisor`
        The Supervisor player that runs the project. Defaults to `None`.
    prefs : `list`
        A list of `Player` instances in the order of the project's supervisor
        preferences.
    pref_names : `list`
        A list of the names in `prefs`. Updates with `prefs`.
    matching : `list`
        The current matches of the project. An empty list if currently
        unsubscribed.
    """

    def __init__(self, name, capacity):

        super().__init__(name, capacity)
        self.supervisor = None

    def set_supervisor(self, supervisor):
        """ Set the project's supervisor member, add the project to their list
        of active projects and increment their capacity. """

        self.supervisor = supervisor
        if self not in supervisor.projects:
            supervisor.projects.append(self)

    def match(self, student):
        """ Match the project to a student, and update the project's supervisor's
        matching, too. """

        self.matching.append(student)
        self.matching.sort(key=self.prefs.index)
        self.supervisor.match(student)

    def unmatch(self, student):
        """ Break the matching between a project and some student, and the
        matching between them and the supervisor member. """

        matching = self.matching[:]
        matching.remove(student)
        self.matching = matching
        self.supervisor.unmatch(student)

    def forget(self, student):
        """ Remove a student from the preference list of the project and its
        supervisor member. """

        prefs = self.prefs[:]
        prefs.remove(student)
        self.prefs = prefs
        self.supervisor.forget(student)
