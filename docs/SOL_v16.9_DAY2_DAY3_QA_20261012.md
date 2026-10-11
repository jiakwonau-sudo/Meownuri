# MEOWNURI SOL v16.9 · Day 2→3 전환 및 검은 화면 버그 수정 QA

- 날짜: 2026-10-12 (KST)
- 계열: SOL 전용. ASTRA, `main` (GitHub Pages v15.7), SOL v16.8 원본 및 기존 대표 Vercel alias 변경 없음.
- 수정 범위: Day 2 해피엔딩의 Day 3 자동 진입, A/B 자막 선택 유지, Day 3 검은 화면, Day 3→4 자동 전환.
- 판정: **LOCAL PASS / LIVE + ANDROID PARTIAL**. Vercel preview deployment is READY; 실제 Android·WebGL 3D·실제 HTTPS 브라우저 end-to-end 테스트는 미실시.

## 1. 실제 오류 원인

1. v16.8 Day 3 진입은 별도 `agDay3Btn`에 의존했고, `Game.showEnding('third')`에는 다음 날 자동 진행을 연결한 로직이 없었음.
2. Day 3 진입에서 `g.cut={kind:'day3',phase:0,time:0}`을 주입했으나, 게임 엔진 `Game.cutscene(dt)`는 `day3` 타입을 처리하지 않고 일반 집 입장 연출 분기로 진입함. 장면 좌표 `c.start.x`가 정의되지 않아 콘솔에 `TypeError: Cannot read properties of undefined (reading 'x')`가 반복되고 화면 갱신이 중단됨. Chromium 390×844에서 v16.8 원본으로 **재현 성공**.
3. Day 2 완료 후 `g.ending`, 곰 상태, 스토리 잠금이 남아 Day 3 진입 안정성에 영향. Day 3 스테이지 글도 코어 업데이트에 의해 덮어써질 수 있었음.

## 2. 실제 수정

- `g.cutscene(dt)`에 `kind==='day3'` 전용 처리 분기를 추가하여 기존 집 입장 코드 충돌 차단. 기존 나머지 cutscene은 원본 호출.
- 해피엔딩 `'third'`인 경우만 5초 뒤 **A · 자막 / B · 소리** 선택창 자동 진입. 기존 엔딩의 `DAY 3 · 다음 날` 버튼으로 즉시 진입 가능.
- 실패 엔딩은 자동 전환하지 않고 기존 재시작 유지.
- Day 3 시작 시 엔딩 및 곰 잠금 해제, Day 3 제목 정합성 보완, 기존 저장 키·스키마 보존.
- Day 3 엔딩 정리 이후 새 이야기 Day 4로 자동 연결. `Day 4~10` 엔진의 기존 완료/선택 로직 유지.

## 3. 테스트 증거

| TC | 조작 | 결과 |
|---|---|---|
| R-00 | v16.8 수동 Day3 A 진입, 2.5초 경과 | **FAIL 재현**: `Game.cutscene`, `c.start.x` TypeError |
| T-01 | v16.9 해피엔딩 후 5초, A 선택 | **PASS** Day3 진입, 자막 `🐾 발자국이 있다` 실제 표시, 렌더러 크래시 없음 |
| T-02 | v16.9 해피엔딩 후 5초, B 선택 | **PASS** Day3 진입, 자막 숨김 |
| T-03 | 기존 Day3 수동 버튼 → A/B | **PASS** 두 선택 모두 Day3 표시 및 정상 루프 |
| T-04 | 실패 엔딩 `resist` | **PASS** Day 2 유지, 재시작 버튼 유지, 자동 Day3 없음 |
| T-05 | Day3 컷씬 전체, 곰에게 먹이 주기, 마지막 하루 더 머문다 선택 → Day4 | **PASS** `window.MeownuriStory.state.day===4`, 두 선택 DOM 클릭, pageerror 0, 앱 콘솔 render/update error 0 |
| T-06 | v16.9 GitHub 저장본과 로컬 소스 SHA-1 비교 | **PASS** Git blob SHA `adc73ae4bbcd4ae8255e1429c7303fa036361442` 일치 |
| T-07 | Vercel v16.9 feature-branch 미리보기 배포 | **READY** 서버 배포 확인. Android 실제 접속 및 GPU/WebGL QA는 **미검증** |

- T-01~T-04: Chromium Android 모바일 뷰포트 390×844, `about:blank` HTML 주입, localStorage shim, WebGL 불가로 게임의 내장 2D fallback 사용.
- T-05: Day3 스토리 비트 타이머 **120ms→12ms만 테스트 실행 시 임시 단축**. 실제 배포 소스는 원래 120ms. 클라이언트 DOM 클릭으로 선택 수행. 스크린샷으로 Day4 정상 화면 확인.
- T-07: Vercel `READY` 확인. 제한된 실행 환경에서 외부 HTTPS Playwright 실플레이를 실행할 수 없어 원격 실동작은 판정하지 않음.

## 4. 산출물 / 추적

- 원본 v16.8: Google Drive `MEOWNURI_SOL_v16.8_TAP_WOOD_BITE.html`, SHA256 `b93c85d3c4a9fb087d522cee26a793011d11456e282e4d3c2f15d54aa5aee2ec`
- 수정 v16.9 SHA256: `1234202badd5e173cb840d8e0c72a8b32d93f7677dd2a50f6887c94f63c69f7d`
- 원본 v16.9 Google Drive: https://drive.google.com/file/d/1GyIhCQWbex7I4kafTqWWKedsHm_d6lOB/view
- GitHub SOL 전용 브랜치: https://github.com/jiakwonau-sudo/Meownuri/tree/feat/sol-v16.9-day2-day3-autoflow-20261012
- Git commit: https://github.com/jiakwonau-sudo/Meownuri/commit/9cdea8ddd7d5d1ab3311243476883cdf50067906
- Vercel 테스트 URL: https://meownuri-sol-v16-story-preview-of0jocoa1.vercel.app/
- Vercel deployment `dpl_6Dfg9TSy9vmUUkBhX7X4HFdZvYqU`, target preview, READY.

## 5. 다음 테스트 게이트

1. 실제 Android Brave에서 신규 테스트 URL 열기 → Day2 해피엔딩 → 5초 후 A/B 모달 → 자막 A 선택 → Day3 컷씬 실제 화면/터치 확인.
2. 해당 도메인의 저장소는 기존 대표 URL과 별도로 관리되므로 기존 주소의 진행 저장이 **자동 이전되지 않음**. 실제기 테스트 시 새 버전에서 Day2를 다시 플레이할 수 있음.
3. WebGL 3D 정상 기기의 검은 화면 재발, 프레임레이트, Day3~4 실제 배속과 저장/이어하기 검증 후에만 대표 URL 교체를 검토.

**주의:** 이 문서는 특정 버그의 로컬 재현 및 회귀 테스트 근거이며, 게임 전체 프로덕션 완성 판정이 아님.
