# 리팩토링 계획

## 목표
`assemble.py`의 동작(입출력, `test_assemble.py` 테스트 결과)을 그대로 유지하면서 구조를 개선한다.
각 단계마다 `pytest test_assemble.py` 전체 통과를 확인하고 다음 단계로 넘어간다.

## 단계

### 1단계 - 호환성 규칙(rule) 통합
- 현재 `is_valid_check()`와 `test_produced_car()`에 5개 룰이 각각 하드코딩되어 중복됨.
- 위반 사유(사람이 읽을 문자열 포함)를 반환하는 단일 함수(예: `check_compatibility(q0, q1, q2, q3)`)로 통합.
  - 반환값: 위반 없으면 빈 리스트, 위반 있으면 사유 문자열 리스트.
- `is_valid_check()`는 리스트가 비어있는지로 판단하도록 축소.
- `test_produced_car()`는 리스트 내용을 그대로 출력(FAIL/PASS)하도록 변경.
- CLAUDE.md 룰 5개와 1:1 매핑되는 테이블(딕셔너리/튜플 리스트) 형태로 관리해 향후 룰 추가/삭제가 쉽게 되도록 함.

### 2단계 - 매직넘버 → 상수 일관화
- `select_car_type`, `run_produced_car` 등에서 리터럴 숫자(`1`, `2`, `3`)로 분기하는 부분을 기존 상수(`SEDAN`, `GM`, `MANDO`, `BOSCH_S` 등)로 교체.
- 리터럴과 상수가 섞여 있어 가독성이 떨어지는 부분 제거.

### 3단계 - 이름 매핑 데이터화
- `select_car_type/engine/brake/steering`의 반복적인 if/elif + print 패턴을
  `{상수: "표시이름"}` 형태의 딕셔너리 매핑으로 대체.
- `run_produced_car`의 출력부(Car Type/Engine/Brake/Steering 라벨) 도 같은 매핑 재사용.

### 4단계 - 전역 상태 캡슐화
- `q0~q4`, `step` 전역 변수를 `CarBuild` 같은 dataclass 또는 클래스 인스턴스로 이동.
- `select_*` 함수들을 이 객체의 메서드로 옮기거나, 순수 함수로 만들어 인스턴스를 인자로 받도록 변경.
- 전역 변수 의존을 없애 테스트 시 `reset_state` 픽스처 없이도 독립적인 인스턴스 생성만으로 테스트 가능하게 함.

### 5단계 - `show_menu` 데이터 분리
- step별 메뉴 텍스트(타이틀 + 옵션 리스트)를 딕셔너리/리스트 형태의 데이터로 분리.
- `show_menu`는 해당 데이터를 순회하며 출력만 담당하도록 축소.

### 6단계 - 엔진 고장 케이스 정리
- `q1 == 4`(고장난 엔진)는 호환성 규칙이 아닌 별도의 "고장 상태" 체크임을 명확히 분리.
- `run_produced_car` 내 고장 엔진 체크와 `check_compatibility` 로직이 섞이지 않도록 순서/책임 분리.

## 검증 방법
- 각 단계 완료 후 `python -m pytest test_assemble.py -v` 실행, 57개 테스트 전부 PASS 확인.
- 테스트가 실제 동작을 충분히 덮지 못하는 부분이 발견되면 리팩토링 전에 테스트를 먼저 보강.
- 단계별로 별도 커밋을 남겨 회귀 발생 시 원인 단계를 쉽게 특정할 수 있도록 함.
