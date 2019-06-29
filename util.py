import os


def find_file(folder: str, startswith: str, endswith: str):
    candidates = set()
    for file in os.listdir(folder):
        if file.startswith(startswith) and file.endswith(endswith):
            candidates.add(os.path.join(folder, file))
    if len(candidates) != 1:
        raise ValueError
    else:
        return next(iter(candidates))
