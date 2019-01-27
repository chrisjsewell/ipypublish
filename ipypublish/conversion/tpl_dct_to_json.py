import glob, os, json

dir_path = os.path.dirname(os.path.realpath(__file__))
ext = ".tpl.json"
dtype = "tpl"

# TODO finalise

for path in glob.glob(os.path.join(dir_path, "**", "*"+ext)):
    
    with open(path) as fobj:
        data = json.load(fobj)

    # name = os.path.basename(path).replace(ext, "")
    # folder = os.path.basename(os.path.dirname(path))

    # # data["identifier"] = "{0}-{1}".format(folder, name)
    # descript = data.pop("meta_docstring")
    # data["description"] = "\n".join(descript)

    # data["type"] = dtype

    # segments = {}
    # for key in list(data.keys()):
    #     if key not in ["identifier", "description", "$schema", "type", "overwrite"]:
    #         segments[key] = data.pop(key)
    # data["segments"] = segments

    # if folder == "ipypublish":
    #     prefix = "ipy-"
    # else:
    #     prefix = "std-"

    # new_path = os.path.join(os.path.dirname(path), prefix+name+ext)

    data.pop("type")
    data["template"] = "html-tpl"

    with open(path, "w") as fobj:
        json.dump(data, fobj, indent=2)