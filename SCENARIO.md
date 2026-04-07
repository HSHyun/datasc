# SCENARIO.md
# Source: IC_PBL시나리오.pdf + 0장_과목개요.pdf + 2장_데이터전처리.pdf

## Course Context
- 과목: 데이터사이언스 (SCS4001), 한양대학교, 4학년 2학기
- 수업 방식: IC-PBL (Industry-Coupled Problem Based Learning)
- 평가 방식: PBL Module 1 (25%) + PBL Module 2 (25%) + 기말고사 (40%) + 출석 (10%)
- 중간 발표: 8주차 (PBL Module 1)
- 최종 발표: 15주차

## Deliverable (from IC_PBL시나리오.pdf)

### Title
"미국 화물 통계(FAF5) 기반 트럭 운송 수요 예측"

### Scenario
- 의뢰사: NGL USA (물류 회사)
- 역할: NGL Korea 소속 데이터사이언티스트
- 비즈니스 문제: 향후 5년 동안 미국 내 어떤 Origin-Destination 구간에서 트럭 화물 수요 증가가 가장 클지 예측하고, 이를 바탕으로 창고 입지 선정과 차량 선배치 의사결정을 지원

### Primary Dataset
- FAF5 (Freight Analysis Framework v5.7.1), 2018–2024
- 로컬 경로: `/Users/hsh/datasc/FAF5.7.1_2018-2024/FAF5.7.1_2018-2024.csv`
- 출처: https://www.bts.gov/faf
- 포함 내용: 출발지, 도착지, 품목, 운송수단, 물동량, 화물 가치, 연도별 지역 간 화물 흐름

### Recommended External Datasets (optional but encouraged)
- FRED: 주 단위 GDP, 실업률, CPI
- EIA: 지역별 디젤 연료 가격 추세
- Census Bureau: 주별 인구 변화

## Task Pipeline

### Step 1: Data Preprocessing & EDA
- 운송수단이 `Truck`인 행만 필터링
- Origin-Destination 쌍별로 연도별 `Tons`, `Value` 합계 집계
- 주요 화물 구간 지도화 및 연도별 추세 시각화
- 필요 시 이상치 탐지 적용

### Step 2: Feature Engineering
- 출발지와 도착지 간 거리 계산
- 품목 카테고리화
- GDP, 연료비 등 외부 경제지표를 주 단위로 결합

### Step 3: Predictive Modeling & Comparison
- 타깃 변수: 특정 O-D 쌍의 다음 해 화물 톤수
- 구현 대상 모델:
  1. 기준 모델: Linear Regression
  2. 머신러닝 모델: Random Forest Regressor, XGBoost, LightGBM
  3. 선택 사항: LSTM 또는 MLP
- 평가 지표: RMSE, MAE, R² Score
- 모델 성능 비교 후 최적 모델 선택 근거 제시

### Final Output
- 수요 증가가 가장 큰 O-D 구간 예측 결과
- 비즈니스 인사이트: 추천 창고 위치와 fleet sizing 방향

## Chapter 2 Reference: Anomaly Detection Methods
# Step 1 데이터 정제와 이상치 처리에 활용 가능

### Overview
- 이상치 탐지는 일반적인 분포나 패턴에서 크게 벗어나는 관측치를 식별하는 방법
- 핵심 특징: 희소성 (드물게 발생), 이질성 (생성 메커니즘이 다름)

### Methods Covered

#### Z-Score (통계 기반)
- 가우시안 분포 가정
- 규칙: `|z| > 3` 이면 이상치
- 공식: `z = (x - μ) / σ`
- 장점: 빠르고 해석이 쉬움
- 단점: 다변량/비선형 관계 반영 어려움

#### LOF - Local Outlier Factor (밀도 기반)
- 한 점의 지역 밀도를 주변 이웃과 비교
- 단계: k-distance -> k-neighborhood -> reachability distance -> LRD -> LOF score
- `LOF >> 1` 이면 이상치 가능성 높음
- 핵심 아이디어: "주변 점들보다 내 밀도가 얼마나 낮은가?"
- 장점: 밀도가 다른 군집 처리 가능
- 단점: 계산량 큼

#### Isolation Forest (트리 기반)
- 핵심 아이디어: 이상치는 적고 다른 점들과 달라서 랜덤 트리에서 더 빨리 분리됨
- 랜덤 결정트리를 만들고 평균 경로 길이 `h(x)`로 이상치 여부 판단
- 이상치 점수: `s(x,n) = 2^(-E(h(x))/c(n))`
  - `s -> 1`: 이상치에 가까움
  - `s -> 0`: 정상에 가까움
  - `s -> 0.5`: 구분 불명확
- 권장: sample size ≥ 256, tree height는 충분히 크게
- 장점: 대규모 데이터에 효율적
- 단점: 차원이 매우 높으면 성능 저하 가능

#### One-Class SVM (모델 기반)
- 커널 트릭으로 고차원 공간에 매핑
- 데이터와 원점 사이의 마진을 최대화하는 초평면 탐색
- 원점은 유일한 "이상" 기준처럼 취급
- 하이퍼파라미터 `ν (nu)`: 이상치 비율 상한, support vector 비율 하한
- `α_i = 0`: 정상
- `α_i = 1/νl`: 이상치
- `0 < α_i < 1/νl`: 초평면 위의 support vector

#### Autoencoder (딥러닝 기반)
- 정상 데이터만으로 학습
- 입력을 압축 표현으로 인코딩한 뒤 다시 복원
- 복원 오차가 크면 이상치로 판단
- 손실 함수: `L(x) = ||x - f_dec(f_enc(x))||²`
- 고차원 데이터나 비정형 데이터(이미지, 시계열)에 적합

### Method Comparison
| Type | Algorithm | Strength | Weakness |
| --- | --- | --- | --- |
| Statistical | Z-Score, GMM | 빠르고 해석 쉬움 | 복잡한 분포에 약함 |
| Density | LOF | 지역 밀도 차이 반영 | 계산비용 큼 |
| Tree | Isolation Forest | 대규모 데이터에 효율적 | 고차원에서 성능 저하 가능 |
| Deep Learning | Autoencoder | 비선형 패턴 처리 가능 | 학습 시간 길고 해석 어려움 |

## Notes for Codex
- 전체 CSV 적재 전 FAF5 스키마를 먼저 확인
- 컬럼 의미는 FAF5 문서로 검증 후 사용
- `Mode` 컬럼에서 Truck이 문자열이 아니라 코드일 수 있으므로 확인 필요
- O-D 쌍은 주 이름이 아니라 FAF zone code일 수 있음
- 타깃 변수인 next-year tonnage는 연도 이동(time shift)으로 구성해야 함
