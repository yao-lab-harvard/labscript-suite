#####################################################################
#                                                                   #
# versions.py                                                       #
#                                                                   #
# Copyright 2019, Chris Billington                                  #
#                                                                   #
# This file is part of the labscript suite (see                     #
# http://labscriptsuite.org) and is licensed under the Simplified   #
# BSD License. See the license.txt file in the root of the project  #
# for the full license.                                             #
#                                                                   #
#####################################################################
import sys
import os
import importlib
import tokenize
import ast
import setuptools_scm
import packaging.version

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata


class NotFound(object):
    pass


class NoVersionInfo(object):
    pass


class VersionException(RuntimeError):
    pass


class BrokenInstall(RuntimeError):
    pass


ERR_BROKEN_INSTALL = """Multiple metadata files for {package} found in {path}; cannot
reliably get version information. This indicates a previous version of the package was
not properly removed. You may want to uninstall the package, manually delete remaining
metadata files/folders, then reinstall the package.""".replace('\n', ' ')


def get_import_path(import_name):
    """Get which entry in sys.path a module would be imported from, without importing
    it.
    
    Args:
        import_name (str): The module name.

    Raises:
        ModuleNotFoundError: Raised if the module is not installed.
        NotImplementedError: Raised if the module is a "namespace package".
            Support for namepsace packages is not currently availabled.

    Returns:
        str: The path to the folder containing the module.

    """
    spec = importlib.util.find_spec(import_name)
    if spec is None:
        raise ModuleNotFoundError(import_name)
    location = spec.origin
    if location is None:
        # A namespace package
        msg = "Version checking of namespace packages not implemented"
        raise NotImplementedError(msg)
    if spec.parent:
        # A package:
        return os.path.dirname(os.path.dirname(location))
    else:
        # A single-file module:
        return os.path.dirname(location)


def _get_metadata_version(project_name, import_path):
    """Gets the package metadata version.

    Args:
        project_name (str): The package name (e.g. the name used when pip installing
            the package).
        import_path (str): The path to the folder containing the installed package.

    Raises:
        :exc:`BrokenInstall`: Raised if the package installation is corrupted (multiple
            packages matching the given arguments were found). May occur if 
            (un)installation for a particular package version only partially completed.
    
    Returns:
        The metadata version for a package with the given project name located at
        the given import path, or None if there is no such package.
    """
    
    for finder in sys.meta_path:
        if hasattr(finder, 'find_distributions'):
            context = importlib_metadata.DistributionFinder.Context(
                name=project_name, path=[import_path]
            )
            dists = finder.find_distributions(context)
            dists = list(dists)
            if len(dists) > 1:
                msg = ERR_BROKEN_INSTALL.format(package=project_name, path=import_path)
                raise BrokenInstall(msg)
            if dists:
                return dists[0].version


def _get_literal_version(filename):
    """Tokenize a source file and return any :code:`__version__ = <version>` literal 
    defined in it.

    Args:
        filename (str): The path to the file to tokenize.

    Returns:
        Any version literal found matching the above criteria, or None.
    """
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        try:
            tokens = list(tokenize.generate_tokens(f.readline))
        except tokenize.TokenError:
            tokens = []
        for i, token in enumerate(tokens[:-2]):
            token_type, token_str, _, _, _ = token
            if token_type == tokenize.NAME and token_str == '__version__':
                next_token_type, next_token_str, _, _, _ = tokens[i + 1]
                if next_token_type == tokenize.OP and next_token_str == '=':
                    next_next_token_type, next_next_token_str, _, _, _ = tokens[i + 2]
                    if next_next_token_type == tokenize.STRING:
                        try:
                            version = ast.literal_eval(next_next_token_str)
                            if version is not None:
                                return version
                        except (SyntaxError, ValueError):
                            continue


def get_version(import_name, project_name=None, import_path=None):
    """Try very hard to get the version of a package without importing it. 
    
    If import_path is not given, first find where it would be imported from, without
    importing it. Then look for metadata in the same import path with the given project
    name (note: this is not always the same as the import name, it is the name for
    example you would ask pip to install). If that is found, return the version info
    from it. Otherwise look for a :code:`__version__.py` file in the package directory,
    or a :code:`__version__ = <version>` literal defined in the package source (without
    executing it).

    Args:
        import_name (str): The module name.
        project_name (str, optional): The package name (e.g. the name used when pip
            installing the package). This must be specified if it does not match the
            module name.
        import_path (str, optional): The path to the folder containing the installed
            package.

    Raises:
        NotImplementedError: Raised if the module name contains a period. Only 
            top-level packages are supported at this time.

    Returns: 
        The version literal of the package. 
        If the package cannot be found, :class:`NotFound` is returned. 
        If the version cannot be obtained in the above way, or if the version was found
        but was :code:`None`, :class:`NoVersionInfo` is returned.
    """
    if project_name is None:
        project_name = import_name
    if '.' in import_name:
        msg = "Version checking of top-level packages only implemented"
        raise NotImplementedError(msg)
    if import_path is None:
        # Find the path where the module lives:
        try:
            import_path = get_import_path(import_name)
        except ImportError:
            return NotFound
    if not os.path.exists(os.path.join(import_path, import_name)):
        return NotFound
    try:
        # Check if setuptools_scm gives us a version number, for the case that it's a
        # git repo or PyPI tarball:
        return setuptools_scm.get_version(import_path)
    except LookupError:
        pass
    # Check if importlib_metadata knows about this module:
    version = _get_metadata_version(project_name, import_path)
    if version is not None:
        return version
    # Check if it has a version literal defined in a __version__.py file:
    version_dot_py = os.path.join(import_path, import_name, '__version__.py')
    version = _get_literal_version(version_dot_py)
    if version is not None:
        return version
    # check if it has a __version__ literal defined in its main module.
    pkg = os.path.join(import_path, import_name)
    if os.path.isdir(pkg):
        module_file = os.path.join(pkg, '__init__.py')
    else:
        module_file = pkg + '.py'
    version = _get_literal_version(module_file)
    if version is not None:
        return version
    return NoVersionInfo


def check_version(module_name, at_least, less_than, version=None, project_name=None):
    """Checks if a module version is within specified bounds.
    
    Checks that the version of the given module is at least and less than the given
    version strings. This function uses :func:`get_version` to determine version 
    numbers without importing modules. In order to do this, :code:`project_name` must
    be provided if it differs from :code:`module_name`. For example, pyserial is 
    imported as 'serial', but the project name, as passed to a 'pip install' command, 
    is 'pyserial'. Therefore to check the version of pyserial, pass in
    :code:`module_name='serial'` and :code:`project_name='pyserial'`. 
    You can also pass in a version string yourself, in which case no inspection of
    packages will take place.

    Args:
        module_name (str): The name of the module to check.
        at_least (str): The minimum acceptable module version.
        less_than (str): The minimum unacceptable module version. Usually this would be
            the next major version if the package follows 
            `semver <https://semver.org>`_.
        version (str, optional): The current version of the installed package. Useful when the
            package version is stored in a non-standard location.
        project_name (str, optional): The package name (e.g. the name used when pip
            installing the package). This must be specified if it does not match the
            module name.

    Raises:
        :exc:`VersionException`: if the module was not found or its version could not
            be determined.

    """
    if version is None:
        version = get_version(module_name, project_name)

    if version is NotFound:
        raise VersionException('Module {} not found'.format(module_name))

    if version is NoVersionInfo:
        raise VersionException(
            'Could not get version info from module {}'.format(module_name)
        )

    at_least_version, less_than_version, installed_version = [
        packaging.version.parse(v) for v in [at_least, less_than, version]
    ]

    if not at_least_version <= installed_version < less_than_version:
        msg = (
            '{module_name} {version} found. '
            + '{at_least} <= {module_name} < {less_than} required.'
        )
        raise VersionException(msg.format(**locals()))


if __name__ == '__main__':
    assert get_version('subprocess') == NoVersionInfo
    assert get_version('plsgtbg') == NotFound
    assert type(get_version('labscript_utils')) in [str, bytes]
    assert type(get_version('numpy')) in [str, bytes]
    assert type(get_version('serial', 'pyserial')) in [str, bytes]
