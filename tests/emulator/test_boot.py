from pathlib import Path

import pytest

from tests.support.pyboy_session import EmulatorTimeout, PyBoySession, prepare_rom


pytestmark = [pytest.mark.emulator, pytest.mark.smoke]


class FakePyBoy:
    def __init__(self, *_args, **_kwargs) -> None:
        self.stops: list[bool] = []
        self.register_file = type("Registers", (), {"PC": 0x1234})()
        self.memory = {}

    def set_emulation_speed(self, _speed: int) -> None:
        pass

    def tick(self, _count: int, _render: bool) -> bool:
        return True

    def stop(self, save: bool) -> None:
        self.stops.append(save)

    def hook_register(self, *_args) -> None:
        pass

    def button_press(self, _button: str) -> None:
        pass

    def button_release(self, _button: str) -> None:
        pass


def test_production_rom_reaches_title_screen_headlessly(
    repo_root: Path, tmp_path: Path
) -> None:
    prepared = prepare_rom(
        tmp_path,
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
    )
    with PyBoySession(prepared) as session:
        session.wait_for_hook("StartTitleScreen", max_frames=6_000)
        assert "StartTitleScreen" in session.hook_history
    assert session.stopped
    assert not prepared.save.exists()
    assert not prepared.rtc.exists()


def test_session_stops_without_saving_after_assertion(
    repo_root: Path, tmp_path: Path
) -> None:
    prepared = prepare_rom(
        tmp_path,
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
    )
    fake = FakePyBoy()
    with pytest.raises(AssertionError):
        with PyBoySession(prepared, pyboy_factory=lambda *_args, **_kwargs: fake):
            raise AssertionError("synthetic assertion")
    assert fake.stops == [False]


def test_timeout_has_diagnostics_and_stops(
    repo_root: Path, tmp_path: Path
) -> None:
    prepared = prepare_rom(
        tmp_path,
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
    )
    fake = FakePyBoy()
    with pytest.raises(EmulatorTimeout) as error:
        with PyBoySession(
            prepared, pyboy_factory=lambda *_args, **_kwargs: fake
        ) as session:
            session.wait_until(lambda _session: False, 3, "synthetic state")
    message = str(error.value)
    assert "synthetic state" in message
    assert "ROM SHA-256" in message
    assert "frames: 3" in message
    assert fake.stops == [False]
