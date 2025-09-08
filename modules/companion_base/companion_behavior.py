# Basic
import importlib.util

# Custom module
from modules.core.path_manager import PathManager



def load_behavior_tree(companion_name: str):
    # Build the full path to the companion's behavior_tree.py
    module_path = PathManager.get_companions_dir() / companion_name / "behavior_tree.py"
    module_name = f"{companion_name}_behavior_tree"

    # Load the module from the file path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        raise ImportError(f"Cannot load module for {companion_name}")