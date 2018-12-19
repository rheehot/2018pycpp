# ref : Francesco Mosconi, Travis + Anaconda + Jupyter, https://github.com/ghego/travis_anaconda_jupyter

import os
import subprocess
import tempfile

import pytest

from . import get_cpp_from_ipynb as gcpp
from . import check_links_in_ipynb as cli


def check_kernel_spec():
    """
    Present Jupyter kernel spec
    """

    # https://jupyter-client.readthedocs.io/en/latest/api/kernelspec.html
    import jupyter_client.kernelspec as jk

    kernel_spec_manager = jk.KernelSpecManager()

    print(kernel_spec_manager.get_all_specs())


def _exec_notebook(path):
    """
    Run the ipynb file of path

    Raise exception if any error
    """
    # http://nbconvert.readthedocs.io/en/latest/execute_api.html
    # ijstokes et al, Command line execution of a jupyter notebook fails in default Anaconda 4.1, https://github.com/Anaconda-Platform/nb_conda_kernels/issues/34
    # obtain a temporary filename
    with tempfile.NamedTemporaryFile(suffix=".ipynb") as fout:
        # prepare a command running .ipynb file while converting
        args = [
            "jupyter", # name of program
           "nbconvert", # option
           "--to", "notebook", # conver to another ipynb file
           "--execute", # run while convering
           "--ExecutePreprocessor.timeout=1000",
           "--ExecutePreprocessor.kernel_name=python",
           "--output", fout.name, # output file name
           path    # input file name
        ]
        # run the command above
        # and raise if error
        subprocess.check_call(args)


# Prepare a list of ipynb files of the base_path
def make_file_list(path=os.path.abspath(os.path.join(os.path.split(__file__)[0], os.pardir)), ext='ipynb'):

    file_list = []

    # recursive loop
    for root, _, filenames in os.walk(path):
        if not (
                ('.ipynb_checkpoints' in root)
                or ('.git' in root)
                or ('__pycache__'in root)
                or ('.pytest_cache' in root)
            ):
            # files loop
            for filename in filenames:
                if os.path.splitext(filename)[-1].endswith(ext):
                    file_list.append(os.path.join(root, filename))

    return file_list

ipynb_file_list = make_file_list()


# https://docs.pytest.org/en/latest/example/parametrize.html
@pytest.mark.parametrize("filename", ipynb_file_list)
def test_execute_ipynb(filename):
    print(f'execute_ipynb() : {filename}')
    # run .ipynb file
    _exec_notebook(filename)


# https://docs.pytest.org/en/latest/example/parametrize.html
@pytest.mark.parametrize("filename", ipynb_file_list)
def test_cpp_in_ipynb(filename):
    print(f'test_cpp_in_ipynb() : {filename}')
    # separate .cpp code blocks from the ipynb file,
    # build, and run
    assert gcpp.get_cpp_src_from_ipynb(filename)


@pytest.mark.parametrize("filename", ipynb_file_list)
def test_urls_in_ipynb(filename):
    cli.check_links_in_ipynb(filename)
