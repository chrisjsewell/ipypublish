import shutil
import tempfile
import os

from ipypublish.convert.config_manager import iter_all_export_paths
from ipypublish.convert.main import IpyPubMain
from ipypublish.tests import TEST_FILES_DIR


def convert_all(inpath, outpath):
    """ convert notebook using all available plugins """
    for plugin_name, plugin_path in iter_all_export_paths():

        out_folder = tempfile.mkdtemp()
        publish = IpyPubMain(
            config={
                "IpyPubMain": {
                    "conversion": plugin_name,
                    "outpath": out_folder
                }})
        try:
            outdata = publish(str(inpath))

            exporter = outdata["exporter"]
            outpath = outdata["outpath"]

            extension = exporter.file_extension
            out_name = os.path.splitext(
                os.path.basename(str(inpath)))[0] + extension
            outfile = os.path.join(out_folder, out_name)

            if not os.path.exists(outfile):
                raise IOError("could not find: {} for {}".format(
                    outfile, plugin_name))

            shutil.copyfile(outfile, os.path.join(
                str(outpath), plugin_name + extension))

        finally:
            shutil.rmtree(out_folder)


if __name__ == "__main__":

    _inpath = os.path.join(TEST_FILES_DIR, "ipynb1.ipynb")
    _outpath = os.path.join(TEST_FILES_DIR, "ipynb1_converted")
    convert_all(_inpath, _outpath)
