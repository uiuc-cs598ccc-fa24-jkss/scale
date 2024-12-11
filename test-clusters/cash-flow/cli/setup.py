import os
from setuptools import setup, find_packages
from setuptools.command.install import install
from app.utils import update_env_file

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class CustomInstallCommand(install):
    def run(self):
        k8s_home = os.path.realpath(os.path.join(SCRIPT_DIR, "..", "k8s"))
        env_file = os.path.join(SCRIPT_DIR, 'app', '.env')
        os.environ['K8S_HOME'] = k8s_home

        # Update or add the environment variable in the .env file
        update_env_file(env_file, 'K8S_HOME', k8s_home)

        # Continue with the regular installation process
        install.run(self)
setup(
    name='cash-cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'cash = app.cash.cash_cli:cash',  # Points to the 'cash' function in cli/cash/cash_cli.py
            'k8s = app.k8s.main:k8s',    # Points to the 'k8s' function in cli/cash/cash_cli.py
        ],
    },

    cmdclass={
        'install': CustomInstallCommand,
    },
)