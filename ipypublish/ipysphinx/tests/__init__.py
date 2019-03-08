import os


def get_test_source_dir(subfolder=None):
    if subfolder is None:
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'sourcedirs'))
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'sourcedirs', subfolder))
