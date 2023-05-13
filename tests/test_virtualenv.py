from code_it.code_editor.virtualenv_manager import VirtualenvManager
import shutil
import os

def test_virtualenv_manager():
    venv_manager = VirtualenvManager()
    venv_manager.path = "/tmp/test_env"    
    try:
        venv_manager.create_env()
        result = os.listdir(venv_manager.path)
    finally:
        shutil.rmtree(venv_manager.path)

    assert result
