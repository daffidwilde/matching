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

    @classmethod
    def from_utilities(
        cls,
        student_utils,
        supervisor_utils,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    ):
        """
        Create an instance of SP from utility matrices.

        Higher utilities indicate higher preferences. If there are any
        ties, they are broken in order of appearance.

        Parameters
        ----------
        student_utils : np.ndarray
            Student utility matrix.
        supervisor_utils : np.ndarray
            Supervisor utility matrix.
        project_supervisors : np.ndarray
            Project supervisor affiliation vector.
        project_capacities : np.ndarray
            Project capacity vector.
        supervisor_capacities : np.ndarray
            Supervisor capacity vector.

        Returns
        -------
        StudentProject
            An instance of SP with utilities resolved as rank matrices.
        """
        student_ranks = convert.utility_to_rank(student_utils)
        supervisor_ranks = convert.utility_to_rank(supervisor_utils)

        return cls(student_ranks, supervisor_ranks, project_supervisors, project_capacities, supervisor_capacities)

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

        Returns
        -------
        StudentProject
            Game instance.
        """
        students = sorted(student_prefs)
        projects = sorted(project_supervisors)
        supervisors = sorted(supervisor_prefs)

        student_ranks = convert.preference_to_rank(student_prefs, projects).astype(float)
        supervisor_ranks = convert.preference_to_rank(supervisor_prefs, students).astype(float)
        project_supervisor_array = np.array(
            [supervisors.index(project_supervisors[project]) for project in projects]
        )
        project_capacity_array = np.array(
            [project_capacities.get(project, 0) for project in projects]
        )
        supervisor_capacity_array = np.array(
            [supervisor_capacities.get(supervisor, 0) for supervisor in supervisors]
        )

        student_ranks[student_ranks == len(project_capacity_array)] = np.nan
        supervisor_ranks[supervisor_ranks == len(student_ranks)] = np.nan

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

        algorithm_lookup = {
            "student": self._student_optimal,
            "supervisor": self._supervisor_optimal,
        }
        self.matching = matchings.SPMatching(algorithm_lookup[optimal]())

        if self._preference_lookup:
            self._convert_matching_to_preferences()

        return self.matching

    def _student_optimal(self):
        """
        Solve the instance of SP to be student-optimal.

        The student-optimal algorithm is as follows:

        0. Set all students to be unassigned, and every project and
           supervisor to be totally unsubscribed.
        1. Take any student, $s$, that is unassigned and has a non-empty
           preference list, and consider their most preferred project,
           $p$. Let $f$ denote the supervisor that offers $p$. Assign
           $s$ to be matched to $p$ (and thus $f$).
        2. If $p$ is now over-subscribed, find its worst current match,
           $s'$. Unmatch $s'$ and $p$. Else if $f$ is over-subscribed,
           find their worst current match, $s''$, and the project to
           which they are currently matched, $p'$. Unmatch $p'$ and
           $s''$.
        3. If $p$ is at capacity, find their worst current match, $s'$.
           For each successor, $t$, to $s'$ in the preference list of
           $p$, delete the pair $(p, t)$ from the game.
        4. If $f$ is at capacity, find their worst current match, $s'$.
           For each successor, $t$, to $s'$ in the preference list of
           $f$, delete the pair $(f, t)$ from the game.
        5. Go to 1 until there are no such students left, then end.

        Returns
        -------
        dict
            A mapping of projects to their student matches.
        """
        student_ranks = self.student_ranks.copy()
        supervisor_ranks = self.supervisor_ranks.copy()
        project_ranks = self._get_project_ranks()

        self._project_matching = {p: [] for p in range(self.num_projects)}
        self._supervisor_matching = {s: [] for s in range(self.num_supervisors)}
        self._student_matching = {s: None for s in range(self.num_students)}
        self._free_students = set(range(self.num_students))

        while self._free_students:
            student = self._free_students.pop()
            student_rank = student_ranks[student]
            if np.isnan(student_rank).all():
                continue

            project = np.nanargmin(student_rank)
            supervisor = self.project_supervisors[project]

            supervisor_rank = supervisor_ranks[supervisor]
            project_rank = project_ranks[project]
            project_matches = self._project_matching[project]
            supervisor_matches = self._supervisor_matching[supervisor]

            project_matches.append(student)
            supervisor_matches.append(student)
            self._student_matching[student] = project

            if len(project_matches) > self.project_capacities[project]:
                self._handle_over_subscribed_project(
                    project_rank, project_matches, supervisor_matches
                )
            elif len(supervisor_matches) > self.supervisor_capacities[supervisor]:
                self._handle_over_subscribed_supervisor(supervisor_rank, supervisor_matches)

            if len(project_matches) == self.project_capacities[project]:
                self._handle_full_project(project, project_rank, project_matches, student_ranks)

            if len(supervisor_matches) == self.supervisor_capacities[supervisor]:
                self._handle_full_supervisor(
                    supervisor, supervisor_rank, supervisor_matches, student_ranks, project_ranks
                )

        return self._project_matching

    def _get_project_ranks(self):
        """
        Create a rank array for all the projects.

        Each project's ranking is a projection of their supervisor's
        ranking of the students who ranked them.
        """
        mask = ~np.isnan(self.student_ranks)

        return np.where(
            mask.T,
            self.supervisor_ranks[self.project_supervisors[:, None], np.arange(self.num_students)],
            np.nan,
        )

    def _handle_over_subscribed_project(self, project_rank, project_matches, supervisor_matches):
        """Remove the worst match from an over-subscribed project."""
        worst = project_matches.pop(np.nanargmax(project_rank[project_matches]))
        supervisor_matches.remove(worst)
        self._student_matching[worst] = None
        self._free_students.add(worst)

    def _handle_over_subscribed_supervisor(self, supervisor_rank, supervisor_matches):
        """
        Remove the worst match from an over-subscribed supervisor.

        We find the worst-ranked student matched to one of the
        supervisor's projects, and the project to whom they are matched.
        Then unmatch them.
        """
        worst = supervisor_matches.pop(np.nanargmax(supervisor_rank[supervisor_matches]))
        worst_project = self._student_matching[worst]
        self._project_matching[worst_project].remove(worst)
        self._student_matching[worst] = None
        self._free_students.add(worst)

    def _handle_full_project(self, project, project_rank, project_matches, student_ranks):
        """Remove successors to a full project's worst match."""
        worst_match_rank = np.nanmax(project_rank[project_matches])
        successors = np.flatnonzero(project_rank > worst_match_rank)
        if not successors.size:
            return

        student_ranks[successors, project] = np.nan
        project_rank[successors] = np.nan

    def _handle_full_supervisor(
        self, supervisor, supervisor_rank, supervisor_matches, student_ranks, project_ranks
    ):
        """
        Remove successors to a full supervisor's worst match.

        When removing students from a supervisor's ranking, we also
        remove the students from the supervisor's projects' rankings
        (and likewise for the student rankings).
        """
        worst_match_rank = np.nanmax(supervisor_rank[supervisor_matches])
        successors = np.flatnonzero(supervisor_rank > worst_match_rank)
        if not successors.size:
            return

        projects = np.flatnonzero(self.project_supervisors == supervisor)
        student_ranks[np.ix_(successors, projects)] = np.nan
        supervisor_rank[successors] = np.nan
        project_ranks[np.ix_(projects, successors)] = np.nan

    def _supervisor_optimal(self):
        """
        Solve the instance of SP to be supervisor-optimal.

        The supervisor-optimal algorithm is as follows:

        0. Set all students to be unassigned, and every project and
           supervisor to be totally unsubscribed.
        1. Take any supervisor, $f$, that is under-subscribed and for
           whom there is a student-project pair such that the student
           is not currently assigned to an under-subscribed project
           offered by $f$. Consider their most preferred such student,
           $s$, and that student's most preferred such project, $p$.
        2. If $s$ is matched to some project, $p'$, unmatch them. Assign
           $s$ to $p$ (and thus $f$).
        3. For each successor, $q$, to $p$ in the preference list of
           $s$, delete the pair $q$ from the preference list of $s$.
        4. Go to 1 until there are no such supervisors left, then end.

        Returns
        -------
        dict
            A mapping of projects to their student matches.
        """
        student_ranks = self.student_ranks.copy()
        supervisor_ranks = self.supervisor_ranks.copy()

        self._student_matching = {s: None for s in range(self.num_students)}
        self._project_matching = {p: [] for p in range(self.num_projects)}
        self._free_supervisors = set(range(self.num_supervisors))

        while self._free_supervisors:
            supervisor = self._free_supervisors.pop()
            pair = self._get_next_student_project_pair(supervisor, supervisor_ranks, student_ranks)
            if pair is None:
                continue

            student, project = pair

            if (student_project := self._student_matching.get(student)) is not None:
                self._project_matching[student_project].remove(student)
                self._student_matching[student_project] = None

            self._student_matching[student] = project
            self._project_matching[project].append(student)

            student_rank = student_ranks[student]
            successors = np.flatnonzero(student_rank > student_rank[project])
            student_ranks[student, successors] = np.nan

            supervisor_matches = self._get_supervisor_matches(supervisor)
            if len(supervisor_matches) < self.supervisor_capacities[supervisor]:
                self._free_supervisors.add(supervisor)

        return self._project_matching

    def _get_next_student_project_pair(self, supervisor, supervisor_ranks, student_ranks):
        """
        Get the next suitable student-project pair for a supervisor.

        A pair is suitable if the student is not matched to a project
        offered by the supervisor and there is at least one
        under-subscribed project over which the student has a
        preference. If no such pair exists, we return nothing.
        """
        for student in supervisor_ranks[supervisor].argsort():
            student_rank = student_ranks[student]
            for project in student_rank.argsort():
                if (
                    ~np.isnan(student_rank[project])
                    and self.project_supervisors[project] == supervisor
                    and len(self._project_matching[project]) < self.project_capacities[project]
                ):
                    return student, project

    def _get_supervisor_matches(self, supervisor):
        """Get the students assigned to a supervisor's project."""
        return [
            student
            for proj, studs in self._project_matching.items()
            for student in studs
            if self.project_supervisors[proj] == supervisor
        ]

    def _convert_matching_to_preferences(self):
        """
        Convert the matching to a preference list.

        This is done by inverting the matching and then converting it
        to a preference list.
        """
        converted = {}
        students, projects, _ = self._preference_lookup.values()
        for project, student_matches in self.matching.items():
            converted[projects[project]] = [students[student] for student in student_matches]

        self.matching = matchings.SPMatching(converted, keys="projects", values="students")
