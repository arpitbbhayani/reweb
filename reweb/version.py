import semver


def next_version(site):
    version = semver.VersionInfo.parse(site.version)
    version = version.bump_patch()
    if version.patch == 10:
        version = version.bump_minor()
    if version.minor == 10:
        version = version.bump_major()
    return str(version)
