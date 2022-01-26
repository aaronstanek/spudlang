# defined source_version_check function

def get_version_first_index(raw):
    # look for version~~ starting in the first 32 bytes
    # return first index of version if found
    # return None otherwise
    target = b'spudversion~~'
    for first_byte in range(32):
        match = True
        for i in range(len(target)):
            index = first_byte + i
            if index >= len(raw):
                return None
            if raw[index] != target[i]:
                match = False
                break
        if match:
            return first_byte + len(target)
    return None

def get_version_last_index(raw,version_index):
    # look for ~~ to end version
    # throw if hit end of input
    # or 128 byte maximum first
    tilde_count = 0
    # ~ is code 126
    for i in range(130):
        index = version_index + i
        if index >= len(raw):
            raise ValueError("Malformed input, expected ~~ but got end of input")
        if raw[index] == 126:
            tilde_count += 1
            if tilde_count == 2:
                # excluside final index
                return index - 1
        else:
            tilde_count = 0
    raise ValueError("Malformed input, expected ~~ but reached 128 byte limit")

def extract_version(raw):
    # look for version~~ starting in the first 32 bytes
    # return version as bytes if found
    # return None if no version found
    # return b'ERROR' if malformed
    first_index = get_version_first_index(raw)
    if first_index is None:
        return None
    last_index = get_version_last_index(raw,first_index)
    return raw[first_index:last_index]

this_verison = {
    "major": 0,
    "minor": 5,
    "patch": 0
}

def verify_version(version):
    global this_verison
    # compare
    sections = version.split(b'.')
    # we expect 1, 2, or 3 sections
    if len(sections) > 3:
        return False
    # they should all be nonegative integers
    for i in range(len(sections)):
        try:
            sections[i] = int(sections[i].decode("UTF8"))
        except:
            return False
        if sections[i] < 0:
            return False
    # they are all nonnegative integers now
    # pad for exactly 3 sections
    while len(sections) < 3:
        sections.append(0)
    # major version
    if sections[0] != this_verison["major"]:
        return False
    # major versions are the same
    if sections[1] < 5:
        return False
        # because 0.5.0 introduced breaking changes
        # we cannot process any files before this
    if sections[1] < this_verison["minor"]:
        return True
    if sections[1] > this_verison["minor"]:
        return False
    # minor versions are the same
    if sections[2] < this_verison["patch"]:
        return True
    if sections[2] > this_verison["patch"]:
        return False
    # versions are exactly the same
    return True

def source_version_check(raw):
    # raw is a bytes object
    # corresponding to a recently loaded file
    # we want to know if the source file
    # belongs to a compatible version
    # no version indicated will be allowed
    # throws exception on malformed input
    # returns (True,) for compatible and (False,memo) for incompatible
    version = extract_version(raw)
    if version is None:
        return (True,)
    version_compat = verify_version(version)
    if version_compat:
        return (True,)
    else:
        global this_verison
        name = str(this_verison["major"]) + "." + str(this_verison["minor"]) + "." + str(this_verison["patch"])
        return (False,"This is Spudlang version: "+name+" The source reports a version of: "+version.decode("UTF8"))