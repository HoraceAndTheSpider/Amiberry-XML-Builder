##  GENERAL UTILS
##   V1.0    (can we put this in a constant here??)
##
##    now with numbering so that file can be shared between programs.
##     please increment the number for each function added, 
##       and increment the sub-number for each revision of existing function 


import os


def check_inputdirs(inputdirs):
    """Check the Directories to scan are valid on this system.

    Args:
        inputdirs (list): list of directories to scan.
    Returns:
        list of directories.
    Raises:
        ValueError: if a directory is not valid.

    """
    for i, directory in enumerate(inputdirs):

        # Format Directory string for this OS
        directory = os.path.abspath(directory)

        # Check Directory is valid
        if not os.path.isdir(directory):
            raise ValueError('"{}" is not a valid directory on this system'.format(
                directory
            ))

        # Update Directory string in list with trailing "/" or "\" depending on OS
        inputdirs[i] = "{directory}{separator}".format(
            directory=directory,
            separator=os.sep
        )

    return inputdirs


# sorry Olly, i will let you tidy this up :D 
def check_singledir(inputdirs):
    """Check the Directories to scan are valid on this system.

    Args:
        inputdirs (list): list of directories to scan.
    Returns:
        list of directories.
    Raises:
        ValueError: if a directory is not valid.

    """
   # for i, directory in enumerate(inputdirs):

    
        # Format Directory string for this OS
    directory = os.path.abspath(inputdirs)

        # Check Directory is valid
    if not os.path.isdir(directory):
        raise ValueError('"{}" is not a valid directory on this system'.format(
            directory
        ))

        # Update Directory string in list with trailing "/" or "\" depending on OS
    inputdirs = "{directory}{separator}".format(
        directory=directory,
        separator=os.sep
    )

    return inputdirs
