"""
Test to make sure that libraries built with Nimporter can be used effectively.
"""

import sys
from pathlib import Path
from nimporter import (
    NimCompiler, Nimporter, NimporterException, NimLibImporter, NimModImporter
)
import nimporter


def test_coherent_value():
    "Python object is returned from Nim function."

    # NOTE(pebaz): Importing a cached build artifact is fine in this case since
    # the test is whether or not it can be used, which will fail if it cannot ;)
    from pkg1 import mod1
    assert mod1.func1() == 1


def test_docstring():
    "Make sure a Nim library's docstring is maintained."


def test_register_importer():
    "Make sure that the importers registered by Nimporter actually exist."
    assert sys.meta_path[0] == NimLibImporter
    assert sys.meta_path[-1] == NimModImporter


def test_hash():
    "Make sure when a module is modified it's hash is also."
    module = Path('tests/pkg1/mod2.nim')
    Nimporter.update_hash(module)
    original_hash = Nimporter.get_hash(module)
    original_text = module.read_text()
    module.write_text(original_text.replace('World', 'Pebaz'))
    assert Nimporter.hash_file(module) != original_hash
    module.write_text(original_text.replace('Pebaz', 'World'))
    assert Nimporter.hash_file(module) == original_hash


def test_hash_filename():
    "Make sure that the file used to store the hash is the correct path."
    module = Path('tests/pkg1/mod2.nim')
    proper_hash = Path('tests/pkg1/__pycache__/mod2.nim.hash').resolve()
    assert Nimporter.hash_filename(module) == proper_hash


def test_hash_coincides():
    "Make sure an imported Nim module's hash matches the actual source file."
    from pkg1 import mod1
    assert not Nimporter.hash_changed(Path('tests/pkg1/mod1.nim'))


def test_hash_not_there():
    "Make sure an exception is thrown when a module is not hashed."
    try:
        Nimporter.get_hash(Path('tests/lib4/lib4.nim'))
        assert False, 'Exception should have been thrown.'
    except NimporterException:
        "Expected case"


def test_should_compile():
    "Make sure that modules should be (re)compiled or not."
    filename = Path('tests/pkg4/mod4.nim')

    assert not Nimporter.is_hashed(filename)
    assert Nimporter.hash_changed(filename)
    assert not Nimporter.is_built(filename)
    assert not Nimporter.is_cache(filename)
    assert not NimCompiler.pycache_dir(filename).exists()
    assert not Nimporter.IGNORE_CACHE
    assert Nimporter.should_compile(filename)


def test_correct_data_types_from_nim():
    "Make sure that Nim marshals Python objects correctly."
    import pkg5.mod5 as mod5
    
    assert isinstance(mod5.return_bool(), bool)
    assert isinstance(mod5.return_int(), int)
    assert isinstance(mod5.return_float(), float)
    assert isinstance(mod5.return_str(), str)
    assert isinstance(mod5.return_list(), list)
    assert isinstance(mod5.return_dict(), dict)
    assert isinstance(mod5.return_object(), dict)


def test_correct_data_types_to_nim():
    "Make sure that Python marshals Python objects correctly."
    import pkg5.mod5 as mod5

    assert mod5.receive_bool(True)
    assert mod5.receive_int(1)
    assert mod5.receive_float(3.14)
    assert mod5.receive_str('Hello World!')
    assert mod5.receive_list([1, 2, 3])
    assert mod5.receive_dict(dict(Name='Pebaz', Age=25, Alive=True, Height=6.2))
    assert mod5.receive_object(mod5.return_object())
