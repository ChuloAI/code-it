import pytest
from code_it.code_editor.virtualenv_manager import VirtualenvManager
import shutil
import os

@pytest.fixture
def venv_manager():
    venv_manager = VirtualenvManager()
    try:
        yield venv_manager
    finally:
        pass
        shutil.rmtree(venv_manager.path)


def test_virtualenv_manager(venv_manager):
    venv_manager.create_env()
    result = os.listdir(venv_manager.path)
    assert result


def test_virtualenv_manager_install_dependency(venv_manager):
    venv_manager.create_env()
    venv_manager.add_dependency("requests")
    process = venv_manager.install_dependencies()
    process.check_returncode()
