import logging
import string
import random
import os

import venv

logger = logging.getLogger(__name__)

RANDOM_NAME_LENGTH = 64
class VirtualenvManager:
    def __init__(self, name: str = "", base_path="/tmp") -> None:
        if not name:
            name = ""
            for _ in range(RANDOM_NAME_LENGTH):
                population = random.sample([string.ascii_letters, string.digits], k=1)
                char = random.sample(population, k=1)
                name += char[0]
        self.name = name
        self.path = os.path.join(base_path, name)
        self.dependencies = []

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)


    def create_env(self):
        logger.info("Creating virtualenv at path '%s' ", self.path)

        builder = venv.EnvBuilder()
        builder.create(self.path)


    def activate_env(self):
        pass

    def install_dependencies(self):
        pass