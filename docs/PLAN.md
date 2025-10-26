# PLAN

## 1) 목표/성공 기준
- 업비트 기반 비트코인 자동매매 시스템 MVP 완성
  - 실시간 차트 불러오기, 전략 평가, 포지션 관리, 리스크 제어, AI 기반 튜닝 기능 구현
- Asia/Seoul 타임존 기준 모든 타임스탬프를 KST/UTC 동시 기록
- 이벤트 기반 아키텍처로 서비스 간 결합도 최소화 및 확장성 확보
- 모든 매매/전략/리스크 관련 데이터가 PostgreSQL + TimescaleDB 옵션에 정규화 저장
- 관측성 지표(OpenTelemetry → Prometheus/Loki → Grafana)로 주요 KPI 모니터링 가능

## 2) 아키텍처(서비스/데이터 흐름/의존성)
- 서비스 계층
  - 실시간 차트 불러오기 서비스: 업비트 WebSocket/REST → 데이터 정규화 → DB 저장 → `market.candle.ingested` 이벤트 발행
  - 전략 서비스: DB/Redis에서 캔들/틱/지표 로딩 → 변동성 돌파·그리드·터틀 전략 병렬 실행 → `strategy.signal.created` 이벤트 발행
  - 포지션 서비스: 시그널 소비 → 주문 생성/체결 상태머신 관리 → 주문/포지션 DB 기록 → 체결 결과 이벤트 발행
  - 리스크 서비스: 자본/노출/손익 모니터링 → 위반 시 포지션 제한/청산 이벤트 발행
  - AI 서비스: 트레이드 로그/성과 지표 분석 → 전략/리스크 파라미터 조정 제안 및 적용 이벤트 발행
- 데이터/메시지 경로
  - PostgreSQL(TimescaleDB): 캔들, 신호, 포지션, 주문, 리스크 스냅샷, 실험 데이터 저장
  - Redis: 캐시(최근 캔들/지표), Redis Streams 또는 Kafka로 이벤트 버스 운영
  - S3 호환 스토리지: 장기 백업 및 로그/모델 스냅샷 저장
- 공통 의존성
  - FastAPI 기반 각 서비스 REST/gRPC 엔드포인트
  - Pydantic 스키마로 데이터 계약
  - OpenTelemetry SDK → Prometheus/Loki 익스포터
  - 공통 Clock 유틸(NTP 동기화)
  - Docker Compose(로컬) → K8s(운영 준비)

## 3) 변경 범위(디렉터리/파일/스키마)
- `/services/market_ingest/`: 실시간 차트 수집 로직, 업비트 커넥터, 스케줄러
- `/services/strategy/`: 전략 엔진, 전략별 모듈(변동성 돌파, 그리드, 터틀), 시그널 발행자
- `/services/position/`: 주문 라우터, 포지션 상태머신, 체결 추적, 슬리피지 기록
- `/services/risk/`: 리스크 한도 계산, 노출 모니터링, 자동 축소/청산 로직
- `/services/ai/`: 성과 분석, 파라미터 최적화/실험 관리, 제안 워크플로
- `/core/`: 공통 도메인 모델, 이벤트 스키마, 유틸(Clock, DB 커넥터, 메시지 버스)
- `/infra/`: Docker Compose, K8s 매니페스트, GitOps 스크립트, Observability 스택 설정
- `/db/migrations/`: TimescaleDB/Redis 스키마 정의 및 마이그레이션
- `/docs/`: 아키텍처 다이어그램, 운영 가이드, API 스펙
- `/tests/`: 단위/통합/시뮬/백테스트

## 4) 작업 분해(WBS) & 의존성
1. 프로젝트 뼈대 및 공통 컴포넌트
   - FastAPI/Poetry 구조, 공통 설정/Clock/로깅, Pydantic 스키마
   - 의존성: 없음
2. 데이터 계층 구축
   - PostgreSQL + TimescaleDB 스키마 설계, Redis 설정, S3 백업 전략
   - 의존성: (1)
3. 메시지 버스/이벤트 계약 정의
   - Redis Streams/Kafka 토픽 설계, 이벤트 스키마 확정
   - 의존성: (1), (2)
4. 실시간 차트 불러오기 서비스
   - 업비트 커넥터, 데이터 정규화, DB upsert, 이벤트 발행
   - 의존성: (2), (3)
5. 전략 서비스
   - 전략별 로직, 공통 인풋 로더, 시그널 발행
   - 의존성: (3), (4)
6. 포지션 서비스
   - 주문 라우팅, 체결 추적, 상태머신, DB 기록
   - 의존성: (2), (3), (5)
7. 리스크 서비스
   - 리스크 지표 계산, 제한/청산 정책, 이벤트 처리
   - 의존성: (2), (3), (6)
8. AI 서비스
   - 성과 지표 산출, 파라미터 튜닝, 실험 관리
   - 의존성: (2), (5), (7)
9. 관측성/운영 인프라
   - OpenTelemetry, Prometheus, Loki, Grafana, K8s 배포 파이프라인
   - 의존성: (1)~(8)
10. 통합 테스트/백테스트/문서화
    - 단위/통합/E2E 테스트, 시뮬레이션, 운영 문서
    - 의존성: (1)~(9)

## 5) 테스트 전략(단위/통합/E2E, 시뮬/백테스트 포함)
- 단위 테스트
  - 전략 계산 로직, 포지션 상태머신 전이, 리스크 한도 계산, AI 분석 모듈
  - FastAPI 엔드포인트 및 Pydantic 검증
- 통합 테스트
  - 서비스 간 이벤트 흐름(ingest → strategy → position → risk), DB/Redis 상호작용
  - 주문 체결 시나리오(성공/실패/부분 체결), 리스크 위반 처리
- E2E 테스트
  - 샌드박스 모드에서 WebSocket → 전략 → 주문 → 기록까지 풀 체인 확인
  - 모의 거래소/페이퍼 트레이딩 환경 구성
- 시뮬레이션/백테스트
  - 과거 데이터 기반 전략 백테스트 및 포지션 결과 검증
  - 리스크/AI 서비스가 제안하는 파라미터 적용 효과 검증
- 관측성 테스트
  - 메트릭/로그/트레이스 수집 및 대시보드 검증
  - 알림/경보 규칙 시뮬레이션

## 6) 리스크/가정/오픈 이슈
- 업비트 API 레이트 리밋 및 서비스 중단 대응 필요
- 실시간 데이터 지연/손실 시 전략/리스크 결과 왜곡 가능성
- Redis Streams vs Kafka 선택에 따른 운영 복잡도
- KST/UTC 동시 기록 시 타임존 처리 오류 위험
- AI 서비스 자동 파라미터 조정의 검증/승인 프로세스 필요
- TimescaleDB 확장성 및 비용, 백업/복구 전략 세부 설계 미완
- 보안: API 키 보관, 네트워크 분리, 감사 로그 요구사항 추가 확인 필요

## 7) 브랜치/PR 전략 & 롤백 계획
- Git Flow 변형: `main`(안정), `develop`(통합), 기능별 `feature/*`
- 기능 단위 PR, 2인 코드 리뷰 필수, CI(테스트/린트) 통과 조건
- 대규모 변경 시 ADR(Architecture Decision Record) 작성
- 롤백
  - 애플리케이션: Git 태그/릴리스 기록 기반 롤백, 컨테이너 이미지 버전 유지
  - DB: 마이그레이션 도구(예: Alembic) 다운그레이드 스크립트 준비, 백업에서 복구 절차 문서화
  - 메시지 버스: 이벤트 스키마 버저닝, 리플레이/리드 프로세스 대비

## 부록) 다이어그램/레퍼런스
- 다이어그램
  - 이벤트 흐름: 업비트 → Market Ingest → Redis/Kafka → Strategy → Position/Risk → DB/S3
  - 서비스 의존성: 각 서비스와 공통 인프라(데이터베이스, 메시지 버스, 관측성) 간 관계
  - 포지션 상태머신: NEW → OPEN → PARTIAL → CLOSE/FAILED
- 레퍼런스
  - 업비트 Open API 문서
  - FastAPI, Pydantic, Redis Streams/Kafka 공식 문서
  - TimescaleDB, Prometheus, Loki, Grafana 공식 가이드
