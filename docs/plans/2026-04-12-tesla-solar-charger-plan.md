# Tesla Solar Charger Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Dynamically modulate Biancaneve (Tesla Model S) charging amps to absorb solar surplus when home battery SOC >= 95%.

**Architecture:** Pyscript module in HA with FSM (IDLE → WAITING → CHARGING → PAUSED). Pure control logic extracted into testable Python functions under `scripts/`. Pyscript module is thin glue: read sensors → call logic → write actuators.

**Tech Stack:** Python 3.12 (tests), pyscript (HA runtime), pytest (unit tests), HA REST API (integration verification)

**Design doc:** `docs/plans/2026-04-12-tesla-solar-charger-design.md`

---

### Task 1: HA config plumbing — input_boolean kill switch

**Files:**
- Modify: `homeassistant/configuration.yaml:40-64` (input_boolean section)

**Step 1: Add kill switch input_boolean**

In `homeassistant/configuration.yaml`, add under the existing `input_boolean:` block (after `smart_surplus_notified` at line 64):

```yaml
  tesla_solar_charger_enabled:
    name: "Tesla Solar Charger"
    initial: off
    icon: mdi:ev-station
```

**Step 2: Verify HA accepts config**

Run:
```bash
source .env && curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/services/input_boolean/reload"
```
Expected: `[]` (HTTP 200)

Then verify the entity exists:
```bash
source .env && curl -s -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/states/input_boolean.tesla_solar_charger_enabled" | python3.12 -c "import sys,json; s=json.load(sys.stdin); print(s['state'])"
```
Expected: `off`

**Step 3: Commit**

```bash
cd homeassistant && git add configuration.yaml && \
git commit -m "feat: add Tesla Solar Charger kill switch input_boolean"
```

---

### Task 2: Pure control logic — FSM and amp calculation (TDD)

This task extracts the core algorithm into testable pure Python. No HA dependencies.

**Files:**
- Create: `scripts/tesla_solar_charger_logic.py`
- Create: `scripts/test_tesla_solar_charger_logic.py`

**Step 1: Write failing tests for clamp and amp calculation**

Create `scripts/test_tesla_solar_charger_logic.py`:

```python
"""Tests for Tesla Solar Charger pure logic."""
import pytest
from tesla_solar_charger_logic import (
    clamp,
    compute_target_amps,
    TSCState,
    TSCController,
    TSCConfig,
)


class TestClamp:
    def test_within_range(self):
        assert clamp(10, 5, 16) == 10

    def test_below_min(self):
        assert clamp(3, 5, 16) == 5

    def test_above_max(self):
        assert clamp(20, 5, 16) == 16

    def test_at_boundaries(self):
        assert clamp(5, 5, 16) == 5
        assert clamp(16, 5, 16) == 16


class TestComputeTargetAmps:
    """compute_target_amps(grid_kw, amps_now, config) -> int"""

    def test_large_export_increases_amps(self):
        # grid=-5.0 kW (exporting), currently at 7A
        # delta = (-0.2 - (-5.0)) * 1000 / 690 = +6.96 → +7
        # target = 7 + 7 = 14
        result = compute_target_amps(-5.0, 7, TSCConfig())
        assert result == 14

    def test_small_export_no_change(self):
        # grid=-0.2 kW → delta = 0 → no change
        result = compute_target_amps(-0.2, 7, TSCConfig())
        assert result == 7

    def test_import_decreases_amps(self):
        # grid=+1.0 kW (importing), currently at 10A
        # delta = (-0.2 - 1.0) * 1000 / 690 = -1.74 → -2
        # target = 10 - 2 = 8
        result = compute_target_amps(1.0, 10, TSCConfig())
        assert result == 8

    def test_clamped_to_max(self):
        # grid=-12.0 kW, amps=10 → delta=+17 → clamped to 16
        result = compute_target_amps(-12.0, 10, TSCConfig())
        assert result == 16

    def test_clamped_to_min(self):
        # grid=+3.0 kW, amps=6 → delta=-5 → 1 → clamped to 5
        result = compute_target_amps(3.0, 6, TSCConfig())
        assert result == 5

    def test_zero_grid_slight_decrease(self):
        # grid=0.0, target=-0.2 → delta = -0.2*1000/690 = -0.29 → 0
        # No change (rounded to 0)
        result = compute_target_amps(0.0, 10, TSCConfig())
        assert result == 10
```

**Step 2: Run tests to verify they fail**

Run: `cd scripts && python3.12 -m pytest test_tesla_solar_charger_logic.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tesla_solar_charger_logic'`

**Step 3: Write minimal implementation for clamp and compute_target_amps**

Create `scripts/tesla_solar_charger_logic.py`:

```python
"""Tesla Solar Charger — pure control logic (no HA dependencies).

This module implements the FSM and control algorithm for dynamically
modulating Tesla charging amps based on solar surplus.
"""
from dataclasses import dataclass, field
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
```

**Step 4: Run tests to verify they pass**

Run: `cd scripts && python3.12 -m pytest test_tesla_solar_charger_logic.py -v`
Expected: all 8 tests PASS

**Step 5: Write failing tests for FSM transitions**

Append to `scripts/test_tesla_solar_charger_logic.py`:

```python
class TestTSCController:
    def make_inputs(self, **overrides):
        defaults = dict(
            battery_soc=100.0,
            grid_kw=-5.0,
            tesla_online=True,
            tesla_plugged=True,
            tesla_soc=50.0,
            tesla_charge_limit=90.0,
            tesla_charging=False,
            tesla_charger_power_kw=0.0,
            amps_now=0,
            kill_switch=True,
            sun_up=True,
        )
        defaults.update(overrides)
        return defaults

    def test_idle_to_waiting_when_preconditions_met(self):
        ctrl = TSCController(TSCConfig())
        assert ctrl.state == TSCState.IDLE
        action = ctrl.step(self.make_inputs())
        assert ctrl.state == TSCState.WAITING

    def test_idle_stays_idle_when_battery_low(self):
        ctrl = TSCController(TSCConfig())
        action = ctrl.step(self.make_inputs(battery_soc=80.0))
        assert ctrl.state == TSCState.IDLE

    def test_idle_stays_idle_when_kill_switch_off(self):
        ctrl = TSCController(TSCConfig())
        action = ctrl.step(self.make_inputs(kill_switch=False))
        assert ctrl.state == TSCState.IDLE

    def test_idle_stays_idle_when_tesla_offline(self):
        ctrl = TSCController(TSCConfig())
        action = ctrl.step(self.make_inputs(tesla_online=False))
        assert ctrl.state == TSCState.IDLE

    def test_idle_stays_idle_when_night(self):
        ctrl = TSCController(TSCConfig())
        action = ctrl.step(self.make_inputs(sun_up=False))
        assert ctrl.state == TSCState.IDLE

    def test_idle_stays_idle_when_tesla_full(self):
        ctrl = TSCController(TSCConfig())
        action = ctrl.step(self.make_inputs(tesla_soc=90.0, tesla_charge_limit=90.0))
        assert ctrl.state == TSCState.IDLE

    def test_waiting_to_charging_after_sustained_surplus(self):
        ctrl = TSCController(TSCConfig(resume_delay_s=60, loop_interval_s=30))
        ctrl.step(self.make_inputs())  # IDLE → WAITING
        assert ctrl.state == TSCState.WAITING
        ctrl.step(self.make_inputs())  # +30s
        assert ctrl.state == TSCState.WAITING
        ctrl.step(self.make_inputs())  # +60s → CHARGING
        assert ctrl.state == TSCState.CHARGING

    def test_waiting_to_idle_when_no_surplus(self):
        ctrl = TSCController(TSCConfig())
        ctrl.step(self.make_inputs())  # IDLE → WAITING
        assert ctrl.state == TSCState.WAITING
        # grid barely importing → surplus < min
        ctrl.step(self.make_inputs(grid_kw=0.5))
        assert ctrl.state == TSCState.IDLE

    def test_charging_returns_set_amps_action(self):
        ctrl = TSCController(TSCConfig(resume_delay_s=0))
        ctrl.step(self.make_inputs())  # IDLE → WAITING
        action = ctrl.step(self.make_inputs())  # WAITING → CHARGING
        assert ctrl.state == TSCState.CHARGING
        assert action is not None
        assert action["type"] == "set_amps"
        assert 5 <= action["amps"] <= 16

    def test_charging_to_paused_after_sustained_low_surplus(self):
        cfg = TSCConfig(resume_delay_s=0, pause_delay_s=60, loop_interval_s=30)
        ctrl = TSCController(cfg)
        ctrl.step(self.make_inputs())  # → WAITING
        ctrl.step(self.make_inputs())  # → CHARGING
        assert ctrl.state == TSCState.CHARGING
        # surplus drops below min for 60s (2 cycles)
        ctrl.step(self.make_inputs(grid_kw=0.5, amps_now=5))
        assert ctrl.state == TSCState.CHARGING  # still counting
        ctrl.step(self.make_inputs(grid_kw=0.5, amps_now=5))
        assert ctrl.state == TSCState.PAUSED

    def test_charging_to_idle_when_battery_drops(self):
        cfg = TSCConfig(resume_delay_s=0)
        ctrl = TSCController(cfg)
        ctrl.step(self.make_inputs())  # → WAITING
        ctrl.step(self.make_inputs())  # → CHARGING
        action = ctrl.step(self.make_inputs(battery_soc=85.0))
        assert ctrl.state == TSCState.IDLE
        assert action is not None
        assert action["type"] == "stop"

    def test_paused_to_idle_eventually(self):
        cfg = TSCConfig(resume_delay_s=0, pause_delay_s=0)
        ctrl = TSCController(cfg)
        ctrl.step(self.make_inputs())  # → WAITING
        ctrl.step(self.make_inputs())  # → CHARGING
        ctrl.step(self.make_inputs(grid_kw=0.5, amps_now=5))  # → PAUSED
        assert ctrl.state == TSCState.PAUSED
        # still no surplus → IDLE
        ctrl.step(self.make_inputs(grid_kw=0.5))
        assert ctrl.state == TSCState.IDLE
```

**Step 6: Run tests to verify they fail**

Run: `cd scripts && python3.12 -m pytest test_tesla_solar_charger_logic.py::TestTSCController -v`
Expected: FAIL with `cannot import name 'TSCController'`

**Step 7: Implement TSCController FSM**

Append to `scripts/tesla_solar_charger_logic.py`:

```python
@dataclass
class TSCController:
    config: TSCConfig
    state: TSCState = TSCState.IDLE
    _samples_above_min: int = 0
    _samples_below_min: int = 0
    _session_start_ts: float = 0.0
    _api_calls_today: int = 0
    _last_api_call_ts: float = 0.0

    def _preconditions_ok(self, inputs: dict) -> bool:
        if not inputs["kill_switch"]:
            return False
        if not inputs["tesla_online"]:
            return False
        if not inputs["tesla_plugged"]:
            return False
        if not inputs["sun_up"]:
            return False
        if inputs["tesla_soc"] >= inputs["tesla_charge_limit"]:
            return False
        return True

    def _battery_ok_start(self, inputs: dict) -> bool:
        return inputs["battery_soc"] >= self.config.min_battery_soc_start

    def _battery_ok_continue(self, inputs: dict) -> bool:
        return inputs["battery_soc"] >= self.config.min_battery_soc_stop

    def _surplus_above_min(self, inputs: dict) -> bool:
        # estimate surplus: if grid is negative (exporting), surplus = -grid
        # surplus must cover at least min_amps * v_factor / 1000
        min_kw = self.config.min_amps * self.config.v_factor / 1000
        surplus_kw = -inputs["grid_kw"]
        return surplus_kw >= min_kw

    def step(self, inputs: dict) -> dict | None:
        """Execute one control step. Returns an action dict or None.

        Action types:
        - {"type": "set_amps", "amps": int} — set charging amps
        - {"type": "start", "amps": int} — start charging at given amps
        - {"type": "stop"} — stop charging
        - None — no action needed
        """
        if self.state == TSCState.IDLE:
            return self._step_idle(inputs)
        elif self.state == TSCState.WAITING:
            return self._step_waiting(inputs)
        elif self.state == TSCState.CHARGING:
            return self._step_charging(inputs)
        elif self.state == TSCState.PAUSED:
            return self._step_paused(inputs)

    def _step_idle(self, inputs: dict) -> dict | None:
        if self._preconditions_ok(inputs) and self._battery_ok_start(inputs):
            self.state = TSCState.WAITING
            self._samples_above_min = 0
            self._samples_below_min = 0
        return None

    def _step_waiting(self, inputs: dict) -> dict | None:
        if not self._preconditions_ok(inputs) or not self._battery_ok_start(inputs):
            self.state = TSCState.IDLE
            self._samples_above_min = 0
            return None

        if self._surplus_above_min(inputs):
            self._samples_above_min += 1
            elapsed = self._samples_above_min * self.config.loop_interval_s
            if elapsed >= self.config.resume_delay_s:
                self.state = TSCState.CHARGING
                self._session_start_ts = time.time()
                self._samples_below_min = 0
                target = compute_target_amps(
                    inputs["grid_kw"], inputs["amps_now"], self.config
                )
                return {"type": "start", "amps": target}
        else:
            self._samples_above_min = 0
            self.state = TSCState.IDLE
        return None

    def _step_charging(self, inputs: dict) -> dict | None:
        # Hard exits: preconditions or battery hysteresis
        if not self._preconditions_ok(inputs) or not self._battery_ok_continue(inputs):
            self.state = TSCState.IDLE
            self._samples_below_min = 0
            return {"type": "stop"}

        target = compute_target_amps(
            inputs["grid_kw"], inputs["amps_now"], self.config
        )

        if target < self.config.min_amps:
            self._samples_below_min += 1
            elapsed = self._samples_below_min * self.config.loop_interval_s
            if elapsed >= self.config.pause_delay_s:
                self.state = TSCState.PAUSED
                return {"type": "stop"}
            return None
        else:
            self._samples_below_min = 0

        if target == inputs["amps_now"]:
            return None

        return {"type": "set_amps", "amps": target}

    def _step_paused(self, inputs: dict) -> dict | None:
        if not self._preconditions_ok(inputs) or not self._battery_ok_continue(inputs):
            self.state = TSCState.IDLE
            return None

        if self._surplus_above_min(inputs):
            self._samples_above_min += 1
            elapsed = self._samples_above_min * self.config.loop_interval_s
            if elapsed >= self.config.resume_delay_s:
                self.state = TSCState.CHARGING
                self._samples_below_min = 0
                target = compute_target_amps(
                    inputs["grid_kw"], inputs["amps_now"], self.config
                )
                return {"type": "start", "amps": target}
        else:
            self._samples_above_min = 0
            self.state = TSCState.IDLE
        return None
```

**Step 8: Run all tests**

Run: `cd scripts && python3.12 -m pytest test_tesla_solar_charger_logic.py -v`
Expected: all 20 tests PASS

**Step 9: Commit**

```bash
git add scripts/tesla_solar_charger_logic.py scripts/test_tesla_solar_charger_logic.py && \
git commit -m "feat: Tesla Solar Charger pure control logic with tests

FSM (idle/waiting/charging/paused) and proportional amp control.
Extracted as pure Python for testability — no HA dependencies."
```

---

### Task 3: Pyscript module — HA integration layer

**Files:**
- Create: `homeassistant/pyscript/tesla_solar_charger.py`

**Step 1: Create pyscript directory**

```bash
mkdir -p homeassistant/pyscript
```

**Step 2: Write the pyscript module**

Create `homeassistant/pyscript/tesla_solar_charger.py`:

```python
"""Tesla Solar Charger — pyscript module for Home Assistant.

Reads sensors, runs FSM control loop, writes actuators.
Pure logic is inlined from scripts/tesla_solar_charger_logic.py.
"""

# ── Configuration ────────────────────────────────────────────
MIN_AMPS = 5
MAX_AMPS = 16
TARGET_GRID_KW = -0.2
V_FACTOR = 230 * 3  # trifase
LOOP_INTERVAL_S = 30
PAUSE_DELAY_S = 90
RESUME_DELAY_S = 60
MIN_BATTERY_SOC_START = 95.0
MIN_BATTERY_SOC_STOP = 90.0
ANTI_IMPORT_KW = 0.5
ANTI_IMPORT_DELAY_S = 90
MIN_API_INTERVAL_S = 10

# ── Entity IDs ───────────────────────────────────────────────
E_GRID = "sensor.solaredge_grid_power"
E_BATTERY_SOC = "sensor.deye_battery_soc"
E_TESLA_ONLINE = "binary_sensor.biancaneve_online"
E_TESLA_CHARGER_DOOR = "cover.biancaneve_charger_door"
E_TESLA_CHARGING = "binary_sensor.biancaneve_charging"
E_TESLA_CHARGER_POWER = "sensor.biancaneve_charger_power"
E_TESLA_SOC = "sensor.biancaneve_battery"
E_TESLA_CHARGE_LIMIT = "number.biancaneve_charge_limit"
E_TESLA_AMPS = "number.biancaneve_charging_amps"
E_TESLA_CHARGER_SWITCH = "switch.biancaneve_charger"
E_KILL_SWITCH = "input_boolean.tesla_solar_charger_enabled"
E_SUN = "sun.sun"

# ── FSM State ────────────────────────────────────────────────
STATE_IDLE = "idle"
STATE_WAITING = "waiting"
STATE_CHARGING = "charging"
STATE_PAUSED = "paused"

current_state = STATE_IDLE
samples_above_min = 0
samples_below_min = 0
anti_import_counter = 0
api_calls_today = 0
last_api_call_ts = 0.0
session_start_ts = 0.0
session_energy_start = 0.0


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def safe_float(entity_id, default=0.0):
    val = state.get(entity_id)
    if val in (None, "unknown", "unavailable", ""):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def preconditions_ok():
    if state.get(E_KILL_SWITCH) != "on":
        return False
    if state.get(E_TESLA_ONLINE) != "on":
        return False
    if state.get(E_SUN) != "above_horizon":
        return False
    tesla_soc = safe_float(E_TESLA_SOC, 100)
    tesla_limit = safe_float(E_TESLA_CHARGE_LIMIT, 90)
    if tesla_soc >= tesla_limit:
        return False
    return True


def battery_ok_start():
    return safe_float(E_BATTERY_SOC) >= MIN_BATTERY_SOC_START


def battery_ok_continue():
    return safe_float(E_BATTERY_SOC) >= MIN_BATTERY_SOC_STOP


def surplus_above_min():
    grid_kw = safe_float(E_GRID)
    min_kw = MIN_AMPS * V_FACTOR / 1000
    return (-grid_kw) >= min_kw


def compute_target(grid_kw, amps_now):
    delta_kw = TARGET_GRID_KW - grid_kw
    delta_amps = round(delta_kw * 1000 / V_FACTOR)
    return clamp(amps_now + delta_amps, MIN_AMPS, MAX_AMPS)


def set_tesla_amps(amps):
    global api_calls_today, last_api_call_ts
    now = time.time()
    if now - last_api_call_ts < MIN_API_INTERVAL_S:
        return
    number.set_value(entity_id=E_TESLA_AMPS, value=amps)
    api_calls_today += 1
    last_api_call_ts = now


def start_charging(amps):
    global session_start_ts, session_energy_start
    set_tesla_amps(amps)
    if state.get(E_TESLA_CHARGING) != "on":
        switch.turn_on(entity_id=E_TESLA_CHARGER_SWITCH)
    session_start_ts = time.time()
    session_energy_start = safe_float("sensor.biancaneve_energy_added")


def stop_charging():
    switch.turn_off(entity_id=E_TESLA_CHARGER_SWITCH)


def notify_start():
    service.call(
        "media_player", "play_media",
        entity_id="media_player.family_room",
        media_content_id="media-source://media_source/local/Ding Sound 123107.mp3",
        media_content_type="music",
        announce=True,
    )


def notify_stop():
    duration_min = (time.time() - session_start_ts) / 60
    energy = safe_float("sensor.biancaneve_energy_added") - session_energy_start
    msg = f"Carica completata: +{energy:.1f} kWh in {duration_min:.0f} minuti"
    service.call(
        "notify", "persistent_notification",
        title="Tesla Solar Charger",
        message=msg,
    )


def expose_state():
    state.set(
        "sensor.tsc_state", current_state,
        new_attributes={
            "friendly_name": "TSC State",
            "icon": "mdi:ev-station",
        },
    )
    state.set(
        "sensor.tsc_api_calls_today", api_calls_today,
        new_attributes={
            "friendly_name": "TSC API Calls Today",
            "icon": "mdi:api",
        },
    )


@time_trigger("period(now, 30s)")
def tsc_loop():
    global current_state, samples_above_min, samples_below_min, anti_import_counter

    grid_kw = safe_float(E_GRID)
    bat_soc = safe_float(E_BATTERY_SOC)
    amps_now = int(safe_float(E_TESLA_AMPS))
    tesla_power = safe_float(E_TESLA_CHARGER_POWER)

    log.info(
        f"TSC [{current_state.upper()}] grid={grid_kw}kW bat={bat_soc}% "
        f"tesla={tesla_power}kW@{amps_now}A"
    )

    # ── IDLE ──────────────────────────────────────────────
    if current_state == STATE_IDLE:
        if preconditions_ok() and battery_ok_start():
            current_state = STATE_WAITING
            samples_above_min = 0
            samples_below_min = 0

    # ── WAITING ───────────────────────────────────────────
    elif current_state == STATE_WAITING:
        if not preconditions_ok() or not battery_ok_start():
            current_state = STATE_IDLE
            samples_above_min = 0
        elif surplus_above_min():
            samples_above_min += 1
            elapsed = samples_above_min * LOOP_INTERVAL_S
            if elapsed >= RESUME_DELAY_S:
                current_state = STATE_CHARGING
                samples_below_min = 0
                anti_import_counter = 0
                target = compute_target(grid_kw, amps_now)
                start_charging(target)
                notify_start()
                log.info(f"TSC → CHARGING at {target}A")
        else:
            samples_above_min = 0
            current_state = STATE_IDLE

    # ── CHARGING ──────────────────────────────────────────
    elif current_state == STATE_CHARGING:
        # Hard exit: preconditions or battery hysteresis
        if not preconditions_ok() or not battery_ok_continue():
            current_state = STATE_IDLE
            samples_below_min = 0
            anti_import_counter = 0
            stop_charging()
            notify_stop()
            log.info("TSC → IDLE (preconditions/battery)")
        else:
            # Anti-import safety
            if grid_kw > ANTI_IMPORT_KW:
                anti_import_counter += 1
                if anti_import_counter * LOOP_INTERVAL_S >= ANTI_IMPORT_DELAY_S:
                    current_state = STATE_PAUSED
                    stop_charging()
                    log.warning("TSC → PAUSED (anti-import)")
                    anti_import_counter = 0
            else:
                anti_import_counter = 0

            target = compute_target(grid_kw, amps_now)

            if target < MIN_AMPS:
                samples_below_min += 1
                elapsed = samples_below_min * LOOP_INTERVAL_S
                if elapsed >= PAUSE_DELAY_S:
                    current_state = STATE_PAUSED
                    stop_charging()
                    notify_stop()
                    log.info("TSC → PAUSED (low surplus)")
            else:
                samples_below_min = 0
                if target != amps_now:
                    set_tesla_amps(target)
                    log.info(f"TSC amps {amps_now}→{target}")

    # ── PAUSED ────────────────────────────────────────────
    elif current_state == STATE_PAUSED:
        if not preconditions_ok() or not battery_ok_continue():
            current_state = STATE_IDLE
            samples_above_min = 0
        elif surplus_above_min():
            samples_above_min += 1
            elapsed = samples_above_min * LOOP_INTERVAL_S
            if elapsed >= RESUME_DELAY_S:
                current_state = STATE_CHARGING
                samples_below_min = 0
                anti_import_counter = 0
                target = compute_target(grid_kw, amps_now)
                start_charging(target)
                log.info(f"TSC → CHARGING (resume) at {target}A")
        else:
            samples_above_min = 0
            current_state = STATE_IDLE

    expose_state()


@time_trigger("cron(0 0 * * *)")
def tsc_reset_daily():
    """Reset daily API call counter at midnight."""
    global api_calls_today
    api_calls_today = 0
    log.info("TSC daily API counter reset")
```

**Step 3: Commit**

```bash
cd homeassistant && git add pyscript/tesla_solar_charger.py && \
git commit -m "feat: Tesla Solar Charger pyscript module

FSM control loop (30s), proportional amp regulation, 7-layer safety.
Reads grid_power → computes target amps → writes to Tesla API."
```

---

### Task 4: Enable pyscript in HA configuration

**Files:**
- Modify: `homeassistant/configuration.yaml` (top-level, add `pyscript:` key)

**Step 1: Add pyscript to configuration.yaml**

Add after the `scene:` include line (around line 31):

```yaml
pyscript: !include pyscript/config.yaml
```

**Step 2: Create minimal pyscript config**

Create `homeassistant/pyscript/config.yaml`:

```yaml
allow_all_imports: true
```

**Step 3: Commit**

```bash
cd homeassistant && git add configuration.yaml pyscript/config.yaml && \
git commit -m "feat: enable pyscript integration in HA config"
```

**Step 4: Verify pyscript loads (requires HACS + pyscript installed on HA)**

Note: pyscript must be installed via HACS on the HA instance first. If not installed:
1. Open HA → HACS → Integrations → search "pyscript" → Install
2. Restart HA
3. Then the `pyscript:` config will be picked up

After install, verify:
```bash
source .env && curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/services/pyscript/reload" -w "HTTP %{http_code}\n"
```
Expected: `[]HTTP 200`

Then verify entity exposed:
```bash
source .env && curl -s -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/states/sensor.tsc_state" | python3.12 -c \
  "import sys,json; print(json.load(sys.stdin)['state'])"
```
Expected: `idle`

---

### Task 5: Modify Smart Surplus Advisor — defer to TSC

**Files:**
- Modify: `homeassistant/automations.yaml:1072` (abundance_surplus_detected)
- Modify: `homeassistant/automations.yaml:1401` (abundance_tesla_charge_suggestion)

**Step 1: Add TSC-aware condition to abundance_surplus_detected**

In the `abundance_surplus_detected` automation, add a condition template that skips Tesla surplus suggestions when TSC is actively charging. Find the conditions section and add:

```yaml
    # Skip if Tesla Solar Charger is handling surplus
    - condition: not
      conditions:
        - condition: state
          entity_id: sensor.tsc_state
          state: "charging"
```

**Step 2: Disable Tesla charge suggestion when TSC enabled**

In the `abundance_tesla_charge_suggestion` automation (id: `abundance_tesla_charge_suggestion`), add condition:

```yaml
    # Don't suggest manual Tesla charge when TSC is enabled
    - condition: state
      entity_id: input_boolean.tesla_solar_charger_enabled
      state: "off"
```

**Step 3: Verify config**

```bash
source .env && curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/services/automation/reload" -w "HTTP %{http_code}\n"
```
Expected: `[]HTTP 200`

**Step 4: Commit**

```bash
cd homeassistant && git add automations.yaml && \
git commit -m "feat: Smart Surplus defers to Tesla Solar Charger when active"
```

---

### Task 6: Sonos notification audio (optional, can skip)

**Files:**
- Modify: `scripts/generate_train_announcement.py` (add TSC announcements)

**Step 1: Add TSC announcement to the generator**

Add a new announcement preset for Tesla solar charging start:

```python
ANNOUNCEMENTS["tesla_solar_start"] = {
    "text": "Attenzione, attenzione. Il treno solare per Biancaneve è in partenza. "
            "Ricarica automatica in corso con energia solare.",
    "filename": "tesla_solar_start_announcement.mp3",
}
```

**Step 2: Generate audio**

```bash
python3.12 scripts/generate_train_announcement.py tesla_solar_start
```

**Step 3: Upload to HA media library**

```bash
source .env && curl -s -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -F "media_content_id=media-source://media_source/local/." \
  -F "file=@audio/tesla_solar_start_announcement.mp3" \
  "$HA_URL/api/media_source/local_source/upload"
```

**Step 4: Update pyscript notify_start() to use custom audio**

In `homeassistant/pyscript/tesla_solar_charger.py`, update `notify_start()`:

```python
def notify_start():
    service.call(
        "media_player", "play_media",
        entity_id="media_player.family_room",
        media_content_id="media-source://media_source/local/tesla_solar_start_announcement.mp3",
        media_content_type="music",
        announce=True,
    )
```

**Step 5: Commit**

```bash
git add scripts/generate_train_announcement.py audio/tesla_solar_start_announcement.mp3 && \
cd homeassistant && git add pyscript/tesla_solar_charger.py && \
git commit -m "feat: train-style Sonos announcement for Tesla Solar Charger"
```

---

### Task 7: End-to-end dry-run verification

**Files:** none (read-only verification)

**Step 1: Enable the kill switch**

```bash
source .env && curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"input_boolean.tesla_solar_charger_enabled"}' \
  "$HA_URL/api/services/input_boolean/turn_on"
```

**Step 2: Watch the log for 2 minutes**

```bash
source .env && for i in $(seq 1 4); do
  sleep 30
  curl -s -H "Authorization: Bearer $HA_TOKEN" \
    "$HA_URL/api/states/sensor.tsc_state" | python3.12 -c \
    "import sys,json; s=json.load(sys.stdin); print(f\"TSC: {s['state']}\")"
done
```

Expected progression (if daytime, battery >= 95%, Tesla connected):
```
TSC: waiting
TSC: waiting
TSC: charging
TSC: charging
```

**Step 3: Verify Tesla amps changed**

```bash
source .env && curl -s -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/states/number.biancaneve_charging_amps" | python3.12 -c \
  "import sys,json; s=json.load(sys.stdin); print(f\"Amps: {s['state']}\")"
```

Expected: a value between 5 and 16 matching current surplus.

**Step 4: Disable and verify stop**

```bash
source .env && curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"input_boolean.tesla_solar_charger_enabled"}' \
  "$HA_URL/api/services/input_boolean/turn_off"
```

Wait 30s, then:
```bash
source .env && curl -s -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/states/sensor.tsc_state" | python3.12 -c \
  "import sys,json; s=json.load(sys.stdin); print(f\"TSC: {s['state']}\")"
```

Expected: `TSC: idle`

**Step 5: Final commit (parent repo)**

```bash
cd /Users/fmondora/wip/personal/pedemonte-energy && \
git add homeassistant && \
git commit -m "feat: Tesla Solar Charger — complete implementation

Pyscript FSM loop modulates Biancaneve charging amps to absorb solar surplus.
Activates when home battery >= 95%, CEE 16A trifase (5-16A range).
7-layer safety, Smart Surplus integration, Sonos notifications."
```
