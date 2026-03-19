import json
import shutil
import h5py

SOURCE = "keras_model.h5"
PATCHED = "keras_model_patched.h5"

def clean_layer_config(obj):
    if isinstance(obj, dict):
        if obj.get("class_name") == "DepthwiseConv2D":
            config = obj.get("config", {})
            if "groups" in config:
                print(f"Removing groups from layer: {config.get('name', 'unknown')}")
                config.pop("groups", None)

        for value in obj.values():
            clean_layer_config(value)

    elif isinstance(obj, list):
        for item in obj:
            clean_layer_config(item)

shutil.copyfile(SOURCE, PATCHED)

with h5py.File(PATCHED, "r+") as f:
    model_config = f.attrs.get("model_config")

    if model_config is None:
        raise RuntimeError("No model_config found in H5 file.")

    if isinstance(model_config, bytes):
        model_config = model_config.decode("utf-8")

    config_data = json.loads(model_config)
    clean_layer_config(config_data)

    new_config = json.dumps(config_data)

    if isinstance(f.attrs["model_config"], bytes):
        f.attrs.modify("model_config", new_config.encode("utf-8"))
    else:
        f.attrs.modify("model_config", new_config)

print(f"Patched model saved as: {PATCHED}")