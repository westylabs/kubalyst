from typing import Dict, List
import os
import json

from query.commands import parser
from query.commands.common import Command


THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_DIR = os.path.join(THIS_SCRIPT_DIR, "scripts")


PROPERTIES = json.load(open(os.path.join(SCRIPTS_DIR, "replacements.json"), "r"))


def _templatize_script(
    script_content: str,
    replacements: Dict[str, str],
) -> str:
    intermediate_script = script_content
    for key, value in replacements.items():
        intermediate_script = intermediate_script.replace(
            "${" + key + "}",
            value,
        )
    assert "${" not in intermediate_script
    return intermediate_script


def _parse_script(
    location: str,
    replacements: Dict[str, str] = PROPERTIES,
) -> List[Command]:
    with open(os.path.join(SCRIPTS_DIR, location), "r") as fh:
        file_content = fh.read()

    templalized_content = _templatize_script(
        file_content,
        replacements
    )

    return parser.parse_commands(templalized_content)
    


def test_bootstrap1() -> None:
    commands = _parse_script("bootstrap1.sql")
    assert len(commands) == 7
    

def test_bootstrap2() -> None:
    commands = _parse_script("bootstrap2.sql")
    assert len(commands) == 15


def test_bootstrap3() -> None:
    commands = _parse_script("bootstrap3.sql")
    assert len(commands) == 19


def test_bootstrap4() -> None:
    commands = _parse_script("bootstrap4.sql")
    assert len(commands) == 3


def test_bootstrap5() -> None:
    commands = _parse_script("bootstrap5.sql")
    assert len(commands) == 7   


def test_bootstrap6() -> None:
    commands = _parse_script("bootstrap6.sql")
    assert len(commands) == 12  


def test_bootstrap7() -> None:
    commands = _parse_script("bootstrap7.sql")
    assert len(commands) == 3     


def test_bootstrap8() -> None:
    commands = _parse_script("bootstrap8.sql")
    assert len(commands) == 10   


def test_bootstrap9() -> None:
    commands = _parse_script("bootstrap9.sql")
    assert len(commands) == 4


def test_bootstrap10() -> None:
    commands = _parse_script("bootstrap10.sql")
    assert len(commands) == 5      


def test_bootstrap11() -> None:
    commands = _parse_script("bootstrap11.sql")
    assert len(commands) == 7       


def test_bootstrap12() -> None:
    commands = _parse_script("bootstrap12.sql")
    assert len(commands) == 7                     