"""Tests for Tesla Solar Charger pure control logic."""

import time
import pytest
from tesla_solar_charger_logic import (
    TSCState, TSCConfig, TSCController,
    clamp, compute_target_amps,
)


# --------------- clamp ---------------

class TestClamp:
    def test_within_range(self):
        assert clamp(10, 5, 16) == 10

    def test_below_min(self):
        assert clamp(3, 5, 16) == 5

    def test_above_max(self):
        assert clamp(20, 5, 16) == 16

    def test_at_min_boundary(self):
        assert clamp(5, 5, 16) == 5

    def test_at_max_boundary(self):
        assert clamp(16, 5, 16) == 16


# --------------- compute_target_amps ---------------

class TestComputeTargetAmps:
    def setup_method(self):
        self.cfg = TSCConfig()

    def test_large_export_increases_amps(self):
        # grid_kw=-5.0 means exporting 5 kW, target=-0.2
        # delta_kw = -0.2 - (-5.0) = 4.8 → delta_amps = round(4800/690) = 7
        result = compute_target_amps(-5.0, 5, self.cfg)
        assert result == 12

    def test_small_export_no_change(self):
        # grid_kw=-0.2 matches target exactly → delta=0
        result = compute_target_amps(-0.2, 8, self.cfg)
        assert result == 8

    def test_import_decreases_amps(self):
        # grid_kw=2.0 (importing) → delta_kw = -0.2 - 2.0 = -2.2
        # delta_amps = round(-2200/690) = -3
        result = compute_target_amps(2.0, 10, self.cfg)
        assert result == 7

    def test_clamped_to_max(self):
        result = compute_target_amps(-10.0, 14, self.cfg)
        assert result == 16

    def test_clamped_to_min(self):
        result = compute_target_amps(5.0, 6, self.cfg)
        assert result == 5

    def test_zero_grid(self):
        # grid_kw=0 → delta_kw = -0.2 - 0 = -0.2 → delta_amps = round(-200/690) = 0
        result = compute_target_amps(0.0, 10, self.cfg)
        assert result == 10


# --------------- FSM helpers ---------------

def make_inputs(**overrides) -> dict:
    """Default inputs: all preconditions met, good surplus."""
    defaults = dict(
        battery_soc=98.0,
        grid_kw=-5.0,        # exporting 5 kW
        tesla_online=True,
        tesla_plugged=True,
        tesla_soc=50.0,
        tesla_charge_limit=80.0,
        tesla_charging=False,
        tesla_charger_power_kw=0.0,
        amps_now=0,
        kill_switch=True,
        sun_up=True,
    )
    defaults.update(overrides)
    return defaults


class TestTSCController:
    def setup_method(self):
        self.cfg = TSCConfig()
        self.ctrl = TSCController(self.cfg)

    # --- IDLE transitions ---

    def test_idle_to_waiting_preconditions_ok(self):
        action = self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.WAITING
        assert action is None

    def test_idle_stays_idle_battery_low(self):
        action = self.ctrl.step(make_inputs(battery_soc=80.0))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_idle_stays_idle_kill_switch_off(self):
        action = self.ctrl.step(make_inputs(kill_switch=False))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_idle_stays_idle_tesla_offline(self):
        action = self.ctrl.step(make_inputs(tesla_online=False))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_idle_stays_idle_night(self):
        action = self.ctrl.step(make_inputs(sun_up=False))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_idle_stays_idle_tesla_full(self):
        action = self.ctrl.step(make_inputs(tesla_soc=80.0, tesla_charge_limit=80.0))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_idle_stays_idle_tesla_not_plugged(self):
        action = self.ctrl.step(make_inputs(tesla_plugged=False))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    # --- WAITING transitions ---

    def test_waiting_to_charging_after_sustained_surplus(self):
        # First step: IDLE → WAITING
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.WAITING

        # Simulate time passing beyond resume_delay_s
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1

        action = self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.CHARGING
        assert action is not None
        assert action["type"] == "start"
        assert action["amps"] >= self.cfg.min_amps

    def test_waiting_to_idle_no_surplus(self):
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.WAITING

        # No surplus (importing)
        action = self.ctrl.step(make_inputs(grid_kw=1.0))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_waiting_to_idle_preconditions_fail(self):
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.WAITING

        action = self.ctrl.step(make_inputs(kill_switch=False))
        assert self.ctrl.state == TSCState.IDLE

    # --- CHARGING transitions ---

    def test_charging_returns_set_amps(self):
        # Get to CHARGING state
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.CHARGING

        # Normal charging step with surplus
        action = self.ctrl.step(make_inputs(amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.CHARGING
        assert action is not None
        assert action["type"] == "set_amps"

    def test_charging_to_paused_after_sustained_low_surplus(self):
        # Get to CHARGING
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.CHARGING

        # Low surplus — starts pause timer
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.CHARGING  # not yet

        # Simulate pause delay elapsed
        self.ctrl._deficit_since -= self.cfg.pause_delay_s + 1
        action = self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.PAUSED
        assert action is not None
        assert action["type"] == "stop"

    def test_charging_to_idle_battery_drops(self):
        # Get to CHARGING
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.CHARGING

        # Battery drops below stop threshold (hysteresis)
        action = self.ctrl.step(make_inputs(battery_soc=85.0, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.IDLE
        assert action is not None
        assert action["type"] == "stop"

    def test_charging_to_idle_preconditions_fail(self):
        # Get to CHARGING
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.CHARGING

        action = self.ctrl.step(make_inputs(kill_switch=False, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.IDLE
        assert action is not None
        assert action["type"] == "stop"

    # --- PAUSED transitions ---

    def test_paused_to_charging_surplus_returns(self):
        # Get to PAUSED
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        self.ctrl._deficit_since -= self.cfg.pause_delay_s + 1
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.PAUSED

        # Surplus returns — start timer
        self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.PAUSED  # not yet

        # After resume delay
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        action = self.ctrl.step(make_inputs())
        assert self.ctrl.state == TSCState.CHARGING
        assert action is not None
        assert action["type"] == "start"

    def test_paused_to_idle_no_surplus(self):
        # Get to PAUSED
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        self.ctrl._deficit_since -= self.cfg.pause_delay_s + 1
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.PAUSED

        # Still no surplus — stays paused initially, but surplus_since resets
        # No surplus for extended time → IDLE
        action = self.ctrl.step(make_inputs(grid_kw=1.0))
        assert self.ctrl.state == TSCState.IDLE
        assert action is None

    def test_paused_to_idle_preconditions_fail(self):
        # Get to PAUSED
        self.ctrl.step(make_inputs())
        self.ctrl._surplus_since -= self.cfg.resume_delay_s + 1
        self.ctrl.step(make_inputs())
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        self.ctrl._deficit_since -= self.cfg.pause_delay_s + 1
        self.ctrl.step(make_inputs(grid_kw=1.0, amps_now=8, tesla_charging=True))
        assert self.ctrl.state == TSCState.PAUSED

        action = self.ctrl.step(make_inputs(kill_switch=False))
        assert self.ctrl.state == TSCState.IDLE
