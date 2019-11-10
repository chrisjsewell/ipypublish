
.. An html document created by ipypublish
   outline: ipypublish.templates.outline_schemas/rst_outline.rst.j2
   with segments:
   - nbsphinx-ipypublish-content: ipypublish sphinx content

.. nbinput:: ipython3
    :execution-count: 5
    :no-output:

    import ipywidgets
    label = ipywidgets.HTML()
    label.value = "Hello"
    label

.. only:: html

    .. nboutput:: rst

        .. raw:: html

            <script type="application/vnd.jupyter.widget-view+json">{"model_id": "567cbbb8b92f441a8704ea4a8896b751", "version_major": 2, "version_minor": 0}</script>

.. only:: latex

    .. nboutput::

        HTML(value='Hallo')

.. nbinput:: ipython3
    :execution-count: 7
    :no-output:

    input_text = ipywidgets.Textarea()
    input_text.value = "Hello"
    input_text

.. only:: html

    .. nboutput:: rst

        .. raw:: html

            <script type="application/vnd.jupyter.widget-view+json">{"model_id": "17ac180dd4a84779b2eee1add6ae57ce", "version_major": 2, "version_minor": 0}</script>

.. only:: latex

    .. nboutput::

        Textarea(value='Hallo')

.. nbinput:: ipython3
    :execution-count: 9
    :no-output:

    link = ipywidgets.jslink(
        (label, 'value'),
        (input_text, 'value'))

.. raw:: html

    <script type="application/vnd.jupyter.widget-state+json">
    {"state": {"074f9bae66bb41c4939fe269168c81cb": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonStyleModel", "state": {}}, "0a6fc589e593436485aa29294a2d3f12": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "DescriptionStyleModel", "state": {"description_width": ""}}, "0b0ac26f30284345b16a98ea2f65e3ec": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "0fb56c94b0bf42509bfdeb52d2685fe6": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "17ac180dd4a84779b2eee1add6ae57ce": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "TextareaModel", "state": {"layout": "IPY_MODEL_ecb11562e09a4354bbc412fe8141984b", "style": "IPY_MODEL_447bdef11d09478eb73e52e60903cf43", "value": "Hello"}}, "19922a98931a4f5a96f582bc9309e311": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "19a44d2ac1574ecd856f62599767679d": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonModel", "state": {"layout": "IPY_MODEL_19922a98931a4f5a96f582bc9309e311", "style": "IPY_MODEL_483ce6db6a404e428204c91e6b86f9ff"}}, "1f88a8d40b964fd09097a75dde54f513": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "23caef4d9b8342d2af72a007558d53db": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonStyleModel", "state": {}}, "285a51831f6645c7851afac5fbe4903f": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "LabelModel", "state": {"layout": "IPY_MODEL_907e277227e5473dacfd1e06942fd487", "style": "IPY_MODEL_3e88d22cc99349dbac90ed9483343e15", "value": "Hallo"}}, "2d05ab7bf9bc4785a26c98dbdacf7417": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "TextareaModel", "state": {"layout": "IPY_MODEL_487c730f55a84b4bb59b67faebaaa16c", "style": "IPY_MODEL_0a6fc589e593436485aa29294a2d3f12"}}, "2e5fa6a6ff624f1f97f3c3e6d9a34212": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonStyleModel", "state": {}}, "3e88d22cc99349dbac90ed9483343e15": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "DescriptionStyleModel", "state": {"description_width": ""}}, "447bdef11d09478eb73e52e60903cf43": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "DescriptionStyleModel", "state": {"description_width": ""}}, "47ac16d7a41141b28cce3aa1c6af9b5f": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "LabelModel", "state": {"description": "Hallo", "layout": "IPY_MODEL_0fb56c94b0bf42509bfdeb52d2685fe6", "style": "IPY_MODEL_5dabe6a821db44cc8dc5d534e3ab8164"}}, "483ce6db6a404e428204c91e6b86f9ff": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonStyleModel", "state": {}}, "487c730f55a84b4bb59b67faebaaa16c": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "4ed50195d7a14e8da57fdc3f3d69f810": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonModel", "state": {"layout": "IPY_MODEL_1f88a8d40b964fd09097a75dde54f513", "style": "IPY_MODEL_a150ddee2425493d807bc0dcae7c75c9"}}, "537a83dea36b471cbb61dd977f3f9a98": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "567cbbb8b92f441a8704ea4a8896b751": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "HTMLModel", "state": {"layout": "IPY_MODEL_8e7c46c8882140d1b442aeca10427385", "style": "IPY_MODEL_a43541a7abc747099b77c50de41ae4c8", "value": "Hello"}}, "5dabe6a821db44cc8dc5d534e3ab8164": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "DescriptionStyleModel", "state": {"description_width": ""}}, "669d53a06ed846a685ddda74f0e9336a": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonModel", "state": {"description": "Hallo", "layout": "IPY_MODEL_b924c12db07a455c8bed22b608e2df8b", "style": "IPY_MODEL_074f9bae66bb41c4939fe269168c81cb"}}, "71652fdef80148c4b871fcc19c0a6daa": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonStyleModel", "state": {}}, "7e7b81c9efde4c39bca1edfabec5228b": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "LabelModel", "state": {"description": "Hallo", "layout": "IPY_MODEL_a2d334f57c854964955c292f842a0b18", "style": "IPY_MODEL_acabe332361445d9b5838f6290b1e2a8"}}, "8e7c46c8882140d1b442aeca10427385": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "907e277227e5473dacfd1e06942fd487": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "9f969cb1012b440dbcae193eba7d0754": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "LinkModel", "state": {"source": ["IPY_MODEL_567cbbb8b92f441a8704ea4a8896b751", "value"], "target": ["IPY_MODEL_17ac180dd4a84779b2eee1add6ae57ce", "value"]}}, "a150ddee2425493d807bc0dcae7c75c9": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonStyleModel", "state": {}}, "a2d334f57c854964955c292f842a0b18": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "a43541a7abc747099b77c50de41ae4c8": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "DescriptionStyleModel", "state": {"description_width": ""}}, "acabe332361445d9b5838f6290b1e2a8": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "DescriptionStyleModel", "state": {"description_width": ""}}, "acc4d506800940edbd569adb2c0eec1d": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "b924c12db07a455c8bed22b608e2df8b": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}, "d4c0623dc3f94e0b8ef89b633e91b914": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonModel", "state": {"layout": "IPY_MODEL_0b0ac26f30284345b16a98ea2f65e3ec", "style": "IPY_MODEL_23caef4d9b8342d2af72a007558d53db"}}, "e0ebc1ea89d9478db6501906faccf907": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonModel", "state": {"layout": "IPY_MODEL_537a83dea36b471cbb61dd977f3f9a98", "style": "IPY_MODEL_2e5fa6a6ff624f1f97f3c3e6d9a34212"}}, "e4bd39947b384e9b9f7391a2b313f474": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "ButtonModel", "state": {"description": "Hallo", "layout": "IPY_MODEL_acc4d506800940edbd569adb2c0eec1d", "style": "IPY_MODEL_71652fdef80148c4b871fcc19c0a6daa"}}, "e69bbc94d44445f397b49c89510a351b": {"model_module": "@jupyter-widgets/controls", "model_module_version": "1.5.0", "model_name": "LinkModel", "state": {"source": ["IPY_MODEL_567cbbb8b92f441a8704ea4a8896b751", "value"], "target": ["IPY_MODEL_17ac180dd4a84779b2eee1add6ae57ce", "value"]}}, "ecb11562e09a4354bbc412fe8141984b": {"model_module": "@jupyter-widgets/base", "model_module_version": "1.2.0", "model_name": "LayoutModel", "state": {}}}, "version_major": 2, "version_minor": 0}
    </script>
