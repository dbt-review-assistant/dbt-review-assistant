import pytest

from utils.console_formatting import (
    colour_message,
    check_status_header,
    ConsoleTextColour,
    ConsoleBackgroundColour,
    ConsoleEmphasis,
)


@pytest.mark.parametrize(
    ids=[
        "fail",
        "pass",
        "italic",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "msg": "test message",
                "text_colour": ConsoleTextColour.WHITE,
                "background_colour": ConsoleBackgroundColour.RED,
                "emphasis": ConsoleEmphasis.BOLD,
            },
            "\x1b[1m\x1b[37m\x1b[41mtest message\x1b[0m",
        ),
        (
            {
                "msg": "test message",
                "text_colour": ConsoleTextColour.BLACK,
                "background_colour": ConsoleBackgroundColour.GREEN,
                "emphasis": ConsoleEmphasis.BOLD,
            },
            "\x1b[1m\x1b[30m\x1b[42mtest message\x1b[0m",
        ),
        (
            {
                "msg": "test message",
                "emphasis": ConsoleEmphasis.ITALIC,
            },
            "\x1b[3m\x1b[39m\x1b[49mtest message\x1b[0m",
        ),
    ],
)
def test_colour_message(kwargs, expected_return):
    assert colour_message(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "fail",
        "pass",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "message": "test message",
                "status": False,
            },
            "\x1b[1m\x1b[30m\x1b[41mtest message\x1b[0m",
        ),
        (
            {
                "message": "test message",
                "status": True,
            },
            "\x1b[1m\x1b[37m\x1b[42mtest message\x1b[0m",
        ),
    ],
)
def test_check_status_header(kwargs, expected_return):
    assert check_status_header(**kwargs) == expected_return
