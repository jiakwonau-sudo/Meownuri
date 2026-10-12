# SOL v16.9 Day 4 오버레이 회귀 QA · 2026-10-12

- 범위: `feat/sol-v16.9-day4-hud-dismiss-20261012` 전용.
- 판정: **PASS: 로컬 모바일 2D 18개 + GitHub Actions 소프트웨어 WebGL 3D 모바일 18개.** 두 환경 모두 pageerror 0.
- 코드 수정: `index.html`의 `.sol-guide-dismissed` 전환 효과를 `transition:none!important`로 변경한 한 줄.
- 재현: 원본 닫기 이벤트는 `expanded=false`와 dismissed 클래스를 적용하지만 CSS의 opacity/visibility 180ms 전환 때문에 클릭 직후 computed visibility는 visible이다. 2D에서는 전환 후 hidden이 됐다. GitHub 소프트웨어 WebGL 3D에서는 1.5초 관찰 이후에도 visible이 남았다.
- 기존 테스트는 클릭 직후 hidden을 요구하여 `Close failed`로 종료했다. 상태 관리와 이벤트 연결은 정상이며, 닫힌 패널의 시각적 상태가 뒤늦게 적용되는 것이 원인이다.

## 변경과 검증

1. CSS 한 줄로 닫힘을 즉시 적용. 게임 진행, 저장 스키마, 렌더러는 수정하지 않았다.
2. 실제 HTTP로 해당 커밋의 HTML을 서빙하고 Playwright 모바일 390×844로 테스트한다. `set_content`, localStorage shim, teleport, qaAdvance, 타이머 단축을 사용하지 않는다.
3. 열기 → 즉시 닫기 → HUD 갱신 후 닫힘 유지 → 터치로 다시 열기/닫기 → Escape 닫기 → 다섯 목표까지 걷기/행동 → Day4 완료 → Day5 전환을 확인한다.
4. 기존 CI는 고정된 Vercel 이전 프리뷰를 검사했다. 수정 CI는 체크아웃한 브랜치 소스를 검사하고 SHA256을 로그/결과에 남긴다. 공개 배포 검증과 브랜치 회귀 검증은 구분한다.
5. 테스트에서 140ms HUD 갱신을 기다려 이전 비트의 CTA를 읽고 다음 행동을 오판하지 않도록 했다.

## 증거

- 최초 실패: https://github.com/jiakwonau-sudo/Meownuri/actions/runs/38152542973
- 실패 커밋: `b5a6b590f77f6511cf5f65e9a9c29fb4e09ced8b`
- 코드 수정: https://github.com/jiakwonau-sudo/Meownuri/commit/0c563d9382b4863f79d3147d273a99cb9a2ebe09
- 테스트 보완: https://github.com/jiakwonau-sudo/Meownuri/commit/59899ec9bd89b63c003427c9e405c30b7761ba1a
- 성공 CI (2026-10-12 19:23 KST): https://github.com/jiakwonau-sudo/Meownuri/actions/runs/38235737523
- 수정 HTML SHA256: `d37f9cd3c69abddacb8237bbc6e4efbd3ffe56fb98126502236e7e42b4f616de`
- 회귀 스크립트: `tests/sol_v169_mobile_regression.cjs`
- Actions artifact ID `11740369431`, ZIP SHA256 `d4d17f123bf97fa71ccf1fe52b6bb32e61618b6c5144c1aedb7768d556562ab6`, 만료 2027-01-10 UTC.
- Actions artifact: `sol-v169-day4-hud-qa`의 baseline/fixed 결과 JSON과 Day4/Day5 캡처.
- 원본 재현 CI 38235591441은 원본의 전환 완료를 기다리다 timeout: 수정본 시험은 skipped. 다음 커밋에서 원본 관찰을 진단 기록으로 바꾸고 수정본 회귀 시험을 수행했다.

## 기존 QA 연결 및 한계

- v16.1 Day4~10 PASS는 이전 버전의 별도 시험이다. 이번 v16.9 결과로 소급 변경하지 않는다: [기존 QA](../docs/QA_V16_1_PUBLIC_PLAYTEST.md).
- [기존 QA 검증 기록](../docs/QA_VERIFICATION.md)에 이번 결과를 연결한다.
- [기존 v16.9 Day2/Day3 QA](https://drive.google.com/file/d/1IyBQTFSCWc4yGnUjSsUsSnUKwRXOWEci/view)에 추가 기록한다.
- 실제 Android/Brave 실기기, 하드웨어 GPU, Day1~10 전체 자연 플레이는 미검증.
- 기존 고정 Vercel 프리뷰와 대표 alias는 이번 수정의 배포 대상으로 사용하지 않았다. 해당 URL은 수정본 증거가 아니다.
- ASTRA 계열, main/기존 안정 빌드의 소스와 배포는 변경하지 않았다.

## 최종 체크

| 검증 | 로컬 2D | Actions 3D |
|---|---|---|
| 원본 닫기 실패 재현 | 재현 | 재현 |
| 기본 닫힘/열기/즉시 닫기 | PASS | PASS |
| HUD 갱신 후 닫힘 유지 | PASS | PASS |
| 터치 다시 열기/닫기, Escape | PASS | PASS |
| quiet 접기/복원 | PASS | PASS |
| Day4 다섯 목표 걷기와 실제 행동 | PASS | PASS |
| Day4 완료 → Day5 첫 비트 | PASS | PASS |
| JavaScript pageerror | 0 | 0 |

원본 대비 제품 코드 변경은 CSS 한 줄이며, 테스트 대기 시간을 늘려 닫기 검사를 우회하지 않았다. 닫기 직후 computed visibility=hidden, opacity=0, pointer-events=none을 그대로 요구하여 통과했다.

- 영구 보관 Actions ZIP: https://drive.google.com/file/d/1mE9z351XsqQ5Gz2mTln-OknI0YBBrMmJ/view
- 캡처의 일부 한글은 시험 환경 글꼴 부족으로 네모로 표시된다. 실제 Android 글꼴/시각 품질 판정과 분리한다.
