"""The SP game class and supporting functions."""

import numpy as np

from matching import convert, matchings


class StudentProject:
    """
    Solver for the student-project allocation problem (SP).

    Parameters
    ----------
    student_ranks : np.ndarray
        The rank matrix of all projects by the students.
    supervisor_ranks : np.ndarray
        The rank matrix of all students by the supervisors.
    project_supervisors : np.ndarray
        The project-wise supervisor affiliation array.
    project_capacities : np.ndarray
        Capacity array for the projects.
    supervisor_capacities : np.ndarray
        Capacity array for the supervisors.

    Attributes
    ----------
    num_students : int
        Number of students.
    num_projects : int
        Number of projects.
    num_supervisors : int
        Number of supervisors.
    project_ranks : np.ndarray
        The rank matrix of all students by the projects.
    matching : MultipleMatching or None
        Once the game is solved, a matching is available. This matching
        uses the indices of the project affiliation array as keys and
        the indices of the student ranks as values.
    """

    def __init__(
        self,
        student_ranks,
        supervisor_ranks,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    ):
        self.student_ranks = student_ranks.copy()
        self.supervisor_ranks = supervisor_ranks.copy()
        self.project_supervisors = project_supervisors.copy()
        self.project_capacities = project_capacities.copy()
        self.supervisor_capacities = supervisor_capacities.copy()

        self.num_students = len(student_ranks)
        self.num_projects = len(project_capacities)
        self.num_supervisors = len(supervisor_capacities)
        self.matching = None
        self._preference_lookup = None

        self.check_input_validity()

    @property
    def project_ranks(self):
        """Return the project rank array."""
        mask = self.student_ranks != self.num_projects

        return np.where(
            mask.T,
            self.supervisor_ranks[self.project_supervisors[:, None], np.arange(self.num_students)],
            self.num_students,
        )

    @classmethod
    def from_preferences(
        cls,
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    ):
        """
        Create an instance of SP from preference list dictionaries.

        Each dictionary should contain a strict ordering of the other
        side by each player. The ranking is taken by the order of the
        preference list.

        Parameters
        ----------
        student_prefs : dict
            A dictionary of students and their preferences.
        supervisor_prefs : dict
            A dictionary of supervisors and their preferences.
        project_supervisors : dict
            A dictionary of projects and their supervisors.
        project_capacities : dict
            A dictionary of projects and their capacities.
        supervisor_capacities : dict
            A dictionary of supervisors and their capacities.
        """
        students = sorted(student_prefs)
        projects = sorted(project_supervisors)
        supervisors = sorted(supervisor_prefs)

        student_ranks = convert.preference_to_rank(student_prefs, projects)
        supervisor_ranks = convert.preference_to_rank(supervisor_prefs, students)
        project_supervisor_array = np.array(
            [supervisors.index(project_supervisors[project]) for project in projects]
        )
        project_capacity_array = np.array(
            [project_capacities.get(project, 0) for project in projects]
        )
        supervisor_capacity_array = np.array(
            [supervisor_capacities.get(supervisor, 0) for supervisor in supervisors]
        )

        game = cls(
            student_ranks,
            supervisor_ranks,
            project_supervisor_array,
            project_capacity_array,
            supervisor_capacity_array,
        )
        game._preference_lookup = {
            "students": students,
            "projects": projects,
            "supervisors": supervisors,
        }

        return game

    def check_input_validity(self):
        """Check if any inputs break the rules of the game."""

    def solve(self, optimal="student"):
        """
        Solve the instance of SA.

        The optimality of the matching is with respect to one party and
        is subsequently the worst stable matching for the other party.

        Parameters
        ----------
        optimal : {"student", "supervisor"}, default="student"
            Party for whom to optimise the matching.

        Raises
        ------
        ValueError
            If `optimal` is anything other than the permitted values.

        Returns
        -------
        SPMatching
            A dictionary-like object containing the matching. The keys
            correspond to the projects in the instance, while the values
            are the students matched to each project.
        """
        if optimal not in ("student", "supervisor"):
            raise ValueError(
                f"Invalid choice for `optimal`. "
                f'Must be "student" or "supervisor", not "{optimal}".'
            )

        if optimal == "student":
            matching = self._student_optimal()
        if optimal == "supervisor":
            matching = self._supervisor_optimal()

        self.matching = matchings.SPMatching(matching, keys="projects", values="students")
        if self._preference_lookup:
            self._convert_matching_to_preferences()

        return self.matching

    def _student_optimal(self):
        """
        Solve the instance of SP to be student-optimal.

        The student-optimal algorithm is as follows:

            0. Set all students to be unassigned, and every project and
               supervisor to be totally unsubscribed.
            1. Take any student, $s$, that is unassigned and has a
               non-empty preference list, and consider their most
               preferred project, $p$. Let $f$ denote the supervisor
               that offers $p$. Assign $s$ to be matched to $p$ (and
               thus $f$).
            2. If $p$ is now over-subscribed, find its worst current
               match, $s'$. Unmatch $s'$ and $p$. Else if $f$ is
               over-subscribed, find their worst current match, $s''$,
               and the project to which they are currently matched,
               $p'$. Unmatch $p'$ and $s''$.
            3. If $p$ is now at capacity, find their worst current
               match, $s'$. For each successor, $t$, to $s'$ in the
               preference list of $p$, delete the pair $(p, t)$ from
               the game.
            4. If $f$ is at capacity, find their worst current match,
               $s'$. For each successor, $t$, to $s'$ in the preference
               list of $f$, delete the pair $(f, t)$ from the game.
            5. Go to 1 until there are no such students left, then end.

        Returns
        -------
        dict
            A mapping of projects to their student matches.
        """
        student_ranks = self.student_ranks
        supervisor_ranks = self.supervisor_ranks

        project_matching = {p: [] for p in range(self.num_projects)}
        supervisor_matching = {s: [] for s in range(self.num_supervisors)}
        free_students = set(range(self.num_students))

        while free_students:
            student = free_students.pop()
            student_rank = student_ranks[student]
            if student_rank.min() == self.num_projects:
                continue

            project = student_rank.argmin()
            project_matches = project_matching[project]
            project_rank = self.project_ranks[project]

            supervisor = self.project_supervisors[project]
            supervisor_matches = supervisor_matching[supervisor]
            supervisor_rank = supervisor_ranks[supervisor]

            project_matches.append(student)
            supervisor_matches.append(student)

            if len(project_matches) > self.project_capacities[project]:
                idx = project_rank[project_matches].argmax()
                worst = project_matches[idx]
                del project_matches[idx]
                del supervisor_matches[supervisor_matches.index(worst)]
                free_students.add(worst)

            if len(supervisor_matches) > self.supervisor_capacities[supervisor]:
                idx = supervisor_rank[supervisor_matches].argmax()
                worst = supervisor_matches[idx]
                del supervisor_matches[idx]
                del project_matches[project_matches.index(worst)]
                free_students.add(worst)

            if len(project_matches) == self.project_capacities[project]:
                worst = project_matches[project_rank[project_matches].argmax()]
                successors = np.where(project_rank > project_rank[worst])
                student_ranks[successors, project] = self.num_projects
                supervisor_rank[successors] = self.num_students

            if len(supervisor_matches) == self.supervisor_capacities[supervisor]:
                worst = supervisor_matches[supervisor_rank[supervisor_matches].argmax()]
                successors = np.where(supervisor_rank > supervisor_rank[worst])
                student_ranks[successors, supervisor] = self.num_projects
                supervisor_rank[successors] = self.num_students

        return project_matching

    def _convert_matching_to_preferences(self):
        """Convert the matching to a preference list.

        This is done by inverting the matching and then converting it
        to a preference list.
        """
        converted = {}
        students, projects, _ = self._preference_lookup.values()
        for project, student_matches in self.matching.items():
            converted[projects[project]] = [students[student] for student in student_matches]

        self.matching = matchings.SPMatching(converted, keys="projects", values="students")
