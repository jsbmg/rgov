import os
import pytest

from cleo import Application, CommandTester

from rgov.commands import reindex, paths


application = Application()
application.add(reindex.UpdateIndexCommand())
command = application.find('reindex')
tester = CommandTester(command)

def test_index_exists():
    assert os.path.exists(paths.index_path)

def test_data_path_exists():
    assert os.path.exists(paths.data_folder)
