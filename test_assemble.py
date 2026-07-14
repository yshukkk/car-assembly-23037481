import pytest

import assemble


@pytest.fixture(autouse=True)
def reset_state():
    """각 테스트 전에 선택 상태를 초기화한다."""
    assemble.state.q0 = 0
    assemble.state.q1 = 0
    assemble.state.q2 = 0
    assemble.state.q3 = 0
    assemble.state.q4 = 0
    yield


# ---------------------------------------------------------------------------
# is_valid_range
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ans", [1, 2, 3])
def test_valid_range_step0_ok(ans):
    assert assemble.is_valid_range(assemble.CarType_Q, ans) is True


@pytest.mark.parametrize("ans", [0, 4, -1])
def test_valid_range_step0_out_of_range(ans):
    assert assemble.is_valid_range(assemble.CarType_Q, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2, 3, 4])
def test_valid_range_step1_ok(ans):
    assert assemble.is_valid_range(assemble.Engine_Q, ans) is True


@pytest.mark.parametrize("ans", [-1, 5])
def test_valid_range_step1_out_of_range(ans):
    assert assemble.is_valid_range(assemble.Engine_Q, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2, 3])
def test_valid_range_step2_ok(ans):
    assert assemble.is_valid_range(assemble.brakeSystem_Q, ans) is True


@pytest.mark.parametrize("ans", [-1, 4])
def test_valid_range_step2_out_of_range(ans):
    assert assemble.is_valid_range(assemble.brakeSystem_Q, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2])
def test_valid_range_step3_ok(ans):
    assert assemble.is_valid_range(assemble.SteeringSystem_Q, ans) is True


@pytest.mark.parametrize("ans", [-1, 3])
def test_valid_range_step3_out_of_range(ans):
    assert assemble.is_valid_range(assemble.SteeringSystem_Q, ans) is False


@pytest.mark.parametrize("ans", [0, 1, 2])
def test_valid_range_step4_ok(ans):
    assert assemble.is_valid_range(assemble.Run_Test, ans) is True


@pytest.mark.parametrize("ans", [-1, 3])
def test_valid_range_step4_out_of_range(ans):
    assert assemble.is_valid_range(assemble.Run_Test, ans) is False


# ---------------------------------------------------------------------------
# select_* 함수들이 상태(state)를 올바르게 설정하는지
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ans", [1, 2, 3])
def test_select_car_type_sets_q0(ans):
    assemble.select_car_type(ans)
    assert assemble.state.q0 == ans


@pytest.mark.parametrize("ans", [1, 2, 3, 4])
def test_select_engine_sets_q1(ans):
    assemble.select_engine(ans)
    assert assemble.state.q1 == ans


@pytest.mark.parametrize("ans", [1, 2, 3])
def test_select_brake_sets_q2(ans):
    assemble.select_brake(ans)
    assert assemble.state.q2 == ans


@pytest.mark.parametrize("ans", [1, 2])
def test_select_steering_sets_q3(ans):
    assemble.select_steering(ans)
    assert assemble.state.q3 == ans


# ---------------------------------------------------------------------------
# is_valid_check / test_produced_car - CLAUDE.md 룰 검증
# 룰 1) 제동장치 Bosch -> 조향장치도 Bosch 이어야 함
# 룰 2) Sedan + Continental 제동장치 불가
# 룰 3) SUV + Toyota 엔진 불가
# 룰 4) Truck + WIA 엔진 불가
# 룰 5) Truck + Mando 제동장치 불가
# ---------------------------------------------------------------------------

def _set_state(car, engine, brake, steering):
    assemble.state.q0 = car
    assemble.state.q1 = engine
    assemble.state.q2 = brake
    assemble.state.q3 = steering


def test_valid_check_all_valid_combo_passes():
    # Sedan / GM / Mando / Mobis - 어떤 룰도 위반하지 않음
    _set_state(assemble.SEDAN, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assert assemble.is_valid_check() is True


def test_rule2_sedan_with_continental_brake_fails():
    _set_state(assemble.SEDAN, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_rule3_suv_with_toyota_engine_fails():
    _set_state(assemble.SUV, assemble.TOYOTA, assemble.MANDO, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_rule4_truck_with_wia_engine_fails():
    _set_state(assemble.TRUCK, assemble.WIA, assemble.CONTINENTAL, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_rule5_truck_with_mando_brake_fails():
    _set_state(assemble.TRUCK, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_rule1_bosch_brake_with_non_bosch_steering_fails():
    _set_state(assemble.SUV, assemble.GM, assemble.BOSCH_B, assemble.MOBIS)
    assert assemble.is_valid_check() is False


def test_rule1_bosch_brake_with_bosch_steering_passes():
    _set_state(assemble.SUV, assemble.GM, assemble.BOSCH_B, assemble.BOSCH_S)
    assert assemble.is_valid_check() is True


@pytest.mark.parametrize(
    "car,engine,brake,steering,expected_substr",
    [
        (assemble.SEDAN, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS, "Sedan에는 Continental제동장치 사용 불가"),
        (assemble.SUV, assemble.TOYOTA, assemble.MANDO, assemble.MOBIS, "SUV에는 TOYOTA엔진 사용 불가"),
        (assemble.TRUCK, assemble.WIA, assemble.CONTINENTAL, assemble.MOBIS, "Truck에는 WIA엔진 사용 불가"),
        (assemble.TRUCK, assemble.GM, assemble.MANDO, assemble.MOBIS, "Truck에는 Mando제동장치 사용 불가"),
        (assemble.SUV, assemble.GM, assemble.BOSCH_B, assemble.MOBIS, "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"),
    ],
)
def test_test_produced_car_reports_fail_reason(capsys, car, engine, brake, steering, expected_substr):
    _set_state(car, engine, brake, steering)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert expected_substr in out


def test_test_produced_car_reports_pass(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assemble.test_produced_car()
    out = capsys.readouterr().out
    assert "PASS" in out


# ---------------------------------------------------------------------------
# run_produced_car
# ---------------------------------------------------------------------------

def test_run_produced_car_invalid_combo_does_not_run(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.CONTINENTAL, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "자동차가 동작되지 않습니다" in out
    assert "자동차가 동작됩니다" not in out


def test_run_produced_car_broken_engine_does_not_move(capsys):
    _set_state(assemble.SEDAN, 4, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "엔진이 고장나있습니다" in out
    assert "자동차가 동작됩니다" not in out


def test_run_produced_car_valid_combo_runs(capsys):
    _set_state(assemble.SEDAN, assemble.GM, assemble.MANDO, assemble.MOBIS)
    assemble.run_produced_car()
    out = capsys.readouterr().out
    assert "자동차가 동작됩니다" in out
    assert "Car Type : Sedan" in out
    assert "Engine   : GM" in out
    assert "Brake    : Mando" in out
    assert "Steering : Mobis" in out
