from utils.manifest_object.unit_test import UnitTest


def test_unit_test_original_filepath():
    instance = UnitTest(
        data={"original_filepath": "test_unit_test"},
    )
    assert instance.original_filepath == "test_unit_test"
