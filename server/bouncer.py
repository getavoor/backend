# this file only contains the base function that checks a user agent
# /api/bouncer is defined in routes/api.py

# minimum version code.
MIN_VER_INT = 1
# list of version names to reject.
# note that this is in user agent format, so, for example:
# - "A1.0d" means android client v1.0, debug build,
# - "A1.2.1r" means android client v1.2.1, release build,
# - "I2.3r" means ios client v2.3, release build,
# - "W4.2r" means web client v4.2, release build.
BANNED_VERSIONS = []

def is_version_allowed(ua: str) -> bool:
    """
    Check if the given Planbot version is allowed and supported.

    Parameters
    ----------
    ua : str
        The user agent of the Planbot version to check.
    """
    print("received version: " + ua)
    # reject versions that don't identify themselves as PlanbotPlus
    if not ua.startswith("PlanbotPlus/"):
        print("rejecting: ua identity")
        return False
    # reject pre-closed beta versions (i.e. without version code)
    if " (" not in ua or ")" not in ua:
        print("rejecting: ua malformed")
        return False

    # now, parse the version:
    ver_bits = ua.split(" (")
    # reject invalid user agents
    if len(ver_bits) != 2:
        print("rejecting: too many ua arguments")
        return False
    ver_code = ver_bits[1][:-1]
    # try to read it as a number, reject if it fails
    ver_int = 0
    try:
        ver_int = int(ver_code)
    except ValueError:
        print("rejecting: unparseable ver_int " + ver_code)
        return False

    # reject if the version code is less than the minimum approved version code
    if ver_int < MIN_VER_INT:
        print("rejecting: outdated ver_int")
        return False

    # now, check the version name and reject it if it is blocked:
    ver_name = ver_bits[0][12:] # skip "PlanbotPlus/"
    if ver_name in BANNED_VERSIONS:
        print("rejecting: banned version")
        return False

    # if all is well, approve it
    print("approved")
    return True
