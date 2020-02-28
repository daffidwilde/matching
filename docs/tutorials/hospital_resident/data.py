""" A script to create the dummy data used in `main.ipynb`. """

from collections import defaultdict

import numpy as np
import yaml

NUM_RESIDENTS = 200
CAPACITY = 30
SEED = 0

resident_names = [f"{i:03d}" for i in range(NUM_RESIDENTS)]
hospital_names = [
    "Dewi Sant",
    "Prince Charles",
    "Prince of Wales",
    "Royal Glamorgan",
    "Royal Gwent",
    "St. David",
    "University",
]


def create_resident_to_preferences_map():
    """ Create a map from resident names to an ordered subset of the hospital
    names. """

    resident_to_preference_size = {
        resident: np.random.randint(1, len(hospital_names) + 1)
        for resident in resident_names
    }

    resident_to_preference_idxs = {
        resident: np.random.choice(
            len(hospital_names), size=size, replace=False
        )
        for resident, size in resident_to_preference_size.items()
    }

    resident_to_preferences = {
        resident: np.array(hospital_names)[idxs].tolist()
        for resident, idxs in resident_to_preference_idxs.items()
    }

    return resident_to_preferences


def create_hospital_to_preferences_map(resident_to_preferences):
    """ Create a map from hospital names to a permutation of all those residents
    who ranked them. """

    hospital_to_residents = defaultdict(set)
    for resident, hospitals in resident_to_preferences.items():
        for hospital in hospitals:
            hospital_to_residents[hospital].add(resident)

    hospital_to_preferences = {
        hospital: np.random.permutation(list(residents)).tolist()
        for hospital, residents in hospital_to_residents.items()
    }

    return hospital_to_preferences


def create_hospital_to_capacity_map():
    """ Create a map from hospital names to their capacity. """

    hospital_to_capacity = {hospital: CAPACITY for hospital in hospital_names}

    return hospital_to_capacity


def save_dictionaries_to_yaml(
    resident_preferences, hospital_preferences, capacities
):

    for dictionary, name in zip(
        (resident_preferences, hospital_preferences, capacities),
        ("residents", "hospitals", "capacities"),
    ):
        with open(f"{name}.yml", "w") as f:
            yaml.dump(dictionary, f, indent=4)


def main():
    """ Create the required maps to form the players, and then save them. """

    np.random.seed(SEED)
    print("Seed set:", SEED)

    resident_preferences = create_resident_to_preferences_map()
    hospital_preferences = create_hospital_to_preferences_map(
        resident_preferences
    )
    capacities = create_hospital_to_capacity_map()
    print("Player dictionaries created...")

    save_dictionaries_to_yaml(
        resident_preferences, hospital_preferences, capacities
    )
    print("Dictionaries saved.")


if __name__ == "__main__":
    main()
