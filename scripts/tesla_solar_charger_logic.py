"""Tesla Solar Charger — pure control logic (no HA dependencies).

FSM with states: IDLE → WAITING → CHARGING ⇄ PAUSED
Proportional amp control based on grid export surplus.
"""

from dataclasses import dataclass
from enum import Enum
import time


class TSCState(Enum):
    IDLE = "idle"
    WAITING = "waiting"
    CHARGING = "charging"
    PAUSED = "paused"


@dataclass
class TSCConfig:
    min_amps: int = 5
    max_amps: int = 16
    target_grid_kw: float = -0.2
    v_factor: float = 230 * 3  # trifase
    loop_interval_s: int = 30
    pause_delay_s: int = 90
    resume_delay_s: int = 60
    min_battery_soc_start: float = 95.0
    min_battery_soc_stop: float = 90.0
    anti_import_kw: float = 0.5
    anti_import_delay_s: int = 90
    min_api_interval_s: int = 10
    watchdog_power_zero_s: int = 300


def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def compute_target_amps(grid_kw: float, amps_now: int, config: TSCConfig) -> int:
    delta_kw = config.target_grid_kw - grid_kw
    delta_amps = round(delta_kw * 1000 / config.v_factor)
    return clamp(amps_now + delta_amps, config.min_amps, config.max_amps)


class TSCController:
    """Finite state machine for solar surplus Tesla charging."""

    def __init__(self, config: TSCConfig | None = None):
        self.config = config or TSCConfig()
        self.state = TSCState.IDLE
        self._surplus_since: float = 0.0
        self._deficit_since: float = 0.0

    def _preconditions_ok(self, inputs: dict) -> bool:
        return (
            inputs["kill_switch"]
            and inputs["tesla_online"]
            and inputs["tesla_plugged"]
            and inputs["sun_up"]
            and inputs["tesla_soc"] < inputs["tesla_charge_limit"]
        )

    def _has_surplus(self, inputs: dict) -> bool:
        min_export_kw = self.config.min_amps * self.config.v_factor / 1000
        return -inputs["grid_kw"] >= min_export_kw

    def step(self, inputs: dict) -> dict | None:
        """Run one FSM cycle. Returns an action dict or None."""
        now = time.monotonic()
        cfg = self.config
        preconditions = self._preconditions_ok(inputs)
        surplus = self._has_surplus(inputs)

        if self.state == TSCState.IDLE:
            return self._step_idle(inputs, preconditions, surplus, now)
        elif self.state == TSCState.WAITING:
            return self._step_waiting(inputs, preconditions, surplus, now)
        elif self.state == TSCState.CHARGING:
            return self._step_charging(inputs, preconditions, surplus, now)
        elif self.state == TSCState.PAUSED:
            return self._step_paused(inputs, preconditions, surplus, now)
        return None

    def _step_idle(self, inputs, preconditions, surplus, now) -> dict | None:
        if preconditions and inputs["battery_soc"] >= self.config.min_battery_soc_start:
            self.state = TSCState.WAITING
            self._surplus_since = now if surplus else 0.0
        return None

    def _step_waiting(self, inputs, preconditions, surplus, now) -> dict | None:
        if not preconditions or not surplus:
            self.state = TSCState.IDLE
            self._surplus_since = 0.0
            return None

        if self._surplus_since == 0.0:
            self._surplus_since = now
            return None

        if now - self._surplus_since >= self.config.resume_delay_s:
            self.state = TSCState.CHARGING
            self._deficit_since = 0.0
            amps = compute_target_amps(inputs["grid_kw"], self.config.min_amps, self.config)
            return {"type": "start", "amps": amps}

        return None

    def _step_charging(self, inputs, preconditions, surplus, now) -> dict | None:
        # Hard exits
        if not preconditions or inputs["battery_soc"] < self.config.min_battery_soc_stop:
            self.state = TSCState.IDLE
            self._deficit_since = 0.0
            return {"type": "stop"}

        if not surplus:
            # Track deficit duration
            if self._deficit_since == 0.0:
                self._deficit_since = now
            if now - self._deficit_since >= self.config.pause_delay_s:
                self.state = TSCState.PAUSED
                self._deficit_since = 0.0
                self._surplus_since = 0.0
                return {"type": "stop"}
        else:
            self._deficit_since = 0.0

        # Normal: adjust amps
        amps = compute_target_amps(inputs["grid_kw"], inputs["amps_now"], self.config)
        return {"type": "set_amps", "amps": amps}

    def _step_paused(self, inputs, preconditions, surplus, now) -> dict | None:
        if not preconditions or not surplus:
            self.state = TSCState.IDLE
            self._surplus_since = 0.0
            return None

        if self._surplus_since == 0.0:
            self._surplus_since = now
            return None

        if now - self._surplus_since >= self.config.resume_delay_s:
            self.state = TSCState.CHARGING
            self._deficit_since = 0.0
            amps = compute_target_amps(inputs["grid_kw"], self.config.min_amps, self.config)
            return {"type": "start", "amps": amps}

        return None
