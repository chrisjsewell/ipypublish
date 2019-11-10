def import_sphinx():
    """
    sphinx is an optional extra, so only load it when necessary
    """
    try:
        import sphinx
    except ImportError:
        raise ImportError(
            "Sphinx is not installed. "
            "Please install ipypublish with the sphinx extras: "
            ">> pip install ipypublish[sphinx]"
        )
    if not sphinx.__version__ >= "1.8":
        raise ImportError("Sphinx version must be >= 1.8")
    return sphinx
