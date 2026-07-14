import time
import sys

CLEAR_SCREEN = "\033[H\033[2J"

CAR_TYPE_STEP = 0
ENGINE_STEP = 1
BRAKE_SYSTEM_STEP = 2
STEERING_SYSTEM_STEP = 3
RUN_TEST_STEP = 4

SEDAN = 1
SUV = 2
TRUCK = 3

GM = 1
TOYOTA = 2
WIA = 3

MANDO = 1
CONTINENTAL = 2
BOSCH_B = 3

BOSCH_S = 1
MOBIS = 2

BROKEN_ENGINE = 4

RUN = 1
TEST = 2

CAR_TYPE_NAMES = {SEDAN: "Sedan", SUV: "SUV", TRUCK: "Truck"}
ENGINE_SELECT_NAMES = {GM: "GM", TOYOTA: "TOYOTA", WIA: "WIA", BROKEN_ENGINE: "고장난"}
ENGINE_RUN_NAMES = {GM: "GM", TOYOTA: "TOYOTA", WIA: "WIA"}
BRAKE_SELECT_NAMES = {MANDO: "MANDO", CONTINENTAL: "CONTINENTAL", BOSCH_B: "BOSCH"}
BRAKE_RUN_NAMES = {MANDO: "Mando", CONTINENTAL: "Continental", BOSCH_B: "Bosch"}
STEERING_SELECT_NAMES = {BOSCH_S: "BOSCH", MOBIS: "MOBIS"}
STEERING_RUN_NAMES = {BOSCH_S: "Bosch", MOBIS: "Mobis"}

class CarBuildState:
    def __init__(self):
        self.q0 = 0
        self.q1 = 0
        self.q2 = 0
        self.q3 = 0
        self.q4 = 0

state = CarBuildState()

def delay(ms):
    t = ms / 1000.0
    time.sleep(t)

def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()

CAR_ASCII_ART = [
    "        ______________",
    "       /|            |",
    "  ____/_|_____________|____",
    " |                      O  |",
    " '-(@)----------------(@)--'",
    "===============================",
]

MENU_SCREENS = {
    CAR_TYPE_STEP: {
        "art": CAR_ASCII_ART,
        "title": "어떤 차량 타입을 선택할까요?",
        "options": ["1. Sedan", "2. SUV", "3. Truck"],
    },
    ENGINE_STEP: {
        "title": "어떤 엔진을 탑재할까요?",
        "options": ["0. 뒤로가기", "1. GM", "2. TOYOTA", "3. WIA", "4. 고장난 엔진"],
    },
    BRAKE_SYSTEM_STEP: {
        "title": "어떤 제동장치를 선택할까요?",
        "options": ["0. 뒤로가기", "1. MANDO", "2. CONTINENTAL", "3. BOSCH"],
    },
    STEERING_SYSTEM_STEP: {
        "title": "어떤 조향장치를 선택할까요?",
        "options": ["0. 뒤로가기", "1. BOSCH", "2. MOBIS"],
    },
    RUN_TEST_STEP: {
        "title": "멋진 차량이 완성되었습니다.",
        "options": ["0. 처음 화면으로 돌아가기", "1. RUN", "2. Test"],
    },
}

def show_menu(step):
    clear()
    screen = MENU_SCREENS[step]
    for line in screen.get("art", []):
        print(line)
    print(screen["title"])
    for option in screen["options"]:
        print(option)
    print("===============================")

def is_valid_range(step, ans):
    if step == CAR_TYPE_STEP:
        if ans < SEDAN or ans > TRUCK:
            print("ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능")
            return False
    if step == ENGINE_STEP:
        if ans < 0 or ans > BROKEN_ENGINE:
            print("ERROR :: 엔진은 1 ~ 4 범위만 선택 가능")
            return False
    if step == BRAKE_SYSTEM_STEP:
        if ans < 0 or ans > BOSCH_B:
            print("ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능")
            return False
    if step == STEERING_SYSTEM_STEP:
        if ans < 0 or ans > MOBIS:
            print("ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능")
            return False
    if step == RUN_TEST_STEP:
        if ans < 0 or ans > TEST:
            print("ERROR :: Run 또는 Test 중 하나를 선택 필요")
            return False
    return True

def select_car_type(a):
    state.q0 = a
    name = CAR_TYPE_NAMES.get(a)
    if name:
        print(f"차량 타입으로 {name}을 선택하셨습니다.")

def select_engine(a):
    state.q1 = a
    name = ENGINE_SELECT_NAMES.get(a)
    if name:
        print(f"{name} 엔진을 선택하셨습니다.")

def select_brake(a):
    state.q2 = a
    name = BRAKE_SELECT_NAMES.get(a)
    if name:
        print(f"{name} 제동장치를 선택하셨습니다.")

def select_steering(a):
    state.q3 = a
    name = STEERING_SELECT_NAMES.get(a)
    if name:
        print(f"{name} 조향장치를 선택하셨습니다.")

COMPATIBILITY_RULES = [
    (lambda q0, q1, q2, q3: q0 == SEDAN and q2 == CONTINENTAL,
     "Sedan에는 Continental제동장치 사용 불가"),
    (lambda q0, q1, q2, q3: q0 == SUV and q1 == TOYOTA,
     "SUV에는 TOYOTA엔진 사용 불가"),
    (lambda q0, q1, q2, q3: q0 == TRUCK and q1 == WIA,
     "Truck에는 WIA엔진 사용 불가"),
    (lambda q0, q1, q2, q3: q0 == TRUCK and q2 == MANDO,
     "Truck에는 Mando제동장치 사용 불가"),
    (lambda q0, q1, q2, q3: q2 == BOSCH_B and q3 != BOSCH_S,
     "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"),
]

def check_compatibility(q0, q1, q2, q3):
    return [message for predicate, message in COMPATIBILITY_RULES if predicate(q0, q1, q2, q3)]

def is_valid_check():
    return len(check_compatibility(state.q0, state.q1, state.q2, state.q3)) == 0

def is_engine_broken():
    return state.q1 == BROKEN_ENGINE

def run_produced_car():
    if not is_valid_check():
        print("자동차가 동작되지 않습니다")
        return
    if is_engine_broken():
        print("엔진이 고장나있습니다.")
        print("자동차가 움직이지 않습니다.")
        return

    if state.q0 in CAR_TYPE_NAMES:
        print(f"Car Type : {CAR_TYPE_NAMES[state.q0]}")

    if state.q1 in ENGINE_RUN_NAMES:
        print(f"Engine   : {ENGINE_RUN_NAMES[state.q1]}")

    if state.q2 in BRAKE_RUN_NAMES:
        print(f"Brake    : {BRAKE_RUN_NAMES[state.q2]}")

    if state.q3 in STEERING_RUN_NAMES:
        print(f"Steering : {STEERING_RUN_NAMES[state.q3]}")

    print("자동차가 동작됩니다.")

def test_produced_car():
    violations = check_compatibility(state.q0, state.q1, state.q2, state.q3)
    if violations:
        print("FAIL\n" + violations[0])
    else:
        print("PASS")

def main():
    step = CAR_TYPE_STEP
    while True:
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == 0:
            if step == RUN_TEST_STEP:
                step = CAR_TYPE_STEP
            elif step > CAR_TYPE_STEP:
                step = step - 1
            continue

        if step == CAR_TYPE_STEP:
            select_car_type(ans)
            delay(800)
            step = ENGINE_STEP
        elif step == ENGINE_STEP:
            select_engine(ans)
            delay(800)
            step = BRAKE_SYSTEM_STEP
        elif step == BRAKE_SYSTEM_STEP:
            select_brake(ans)
            delay(800)
            step = STEERING_SYSTEM_STEP
        elif step == STEERING_SYSTEM_STEP:
            select_steering(ans)
            delay(800)
            step = RUN_TEST_STEP
        elif step == RUN_TEST_STEP:
            if ans == RUN:
                run_produced_car()
                delay(2000)
            elif ans == TEST:
                print("Test...")
                delay(1500)
                test_produced_car()
                delay(2000)

if __name__ == "__main__":
    main()
