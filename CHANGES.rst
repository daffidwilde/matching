History
=======

v1.3.0 - 2020-04-17
-------------------

- Update the self-citation information in `paper.bib` to `v1.3`.

v1.3 - 2020-04-14
-----------------

- Players are now copied via `copy.deepcopy` when a game is created and the
  copies are used, leaving any originals unchanged.
- Formalise test and Python requirements in `setup.py`.
- Revert flaky forgetting fix from v1.2.1 and correct the flaky tests that were
  causing the issue.
- Replace the `Game` class with `BaseGame` and make it a metaclass via
  `abc.ABCMeta`.
- Fix bugs in documentation stopping build.

v1.2.1 - 2020-02-28
-------------------

- Finish documentation.
- Complete paper for submission to JOSS.
- Catch flaky forgetting bug in `Player`.

v1.2 - 2020-02-24
-----------------

- Implement the stable roommates problem.
- Add example tests to all games.
- Flesh out documentation.

v1.1 - 2019-05-10
-----------------

- Implemented the student-allocation problem.
- Added capability for large game creation from dictionaries.

v1.0.2 - 2019-01-30
-------------------

- Individuals forget the names of others one at a time rather than all instances
  at once as previously.
- Add citation file.

v1.0.1 - 2019-01-28
-------------------

- Update travis.yml to stop failures. Dodgy support for Python <3.6.
- Add new badges.

v1.0 - 2019-01-22
-----------------

The main changes are as follows:

- Instead of passing dictionaries to an algorithm function, lists of
  `matching.Player` instances must be created for the two matching parties.

- Each of these instances have a few attributes but, most importantly, they take
  a name (this should be unique to the party) and a `list` (or `tuple`) ranking
  their preferences of the names of the other party's members.

- With these lists of `Player` instances, each type of matching game now has its
  own solver class (e.g. the hospital-resident assignment problem uses
  `matching.HospitalResident`) with various methods to solve the game and then
  check the stability/validity of a matching.

Further details given in new `README.rst`.

v0.1 - 2018-03-22
-----------------

First release. Two main algorithm functions for SM and HR.

