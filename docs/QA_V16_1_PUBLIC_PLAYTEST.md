# MEOWNURI 9.0 · SOL v16.1 LIVE PLAYTEST / 2026-10-11



결론: 온라인 테스트 가능한 v16.1 플레이판 배포 및 지정 기능 테스트 PASS. 최종 완성·Android 실기기/3D 품질 판정은 아직 PARTIAL.

계열: SOL 전용. ASTRA 및 GitHub Pages main(v15.7) 변경 없음.



1. PLAY URL

https://meownuri-sol-v16-story-preview.vercel.app/

고정 배포: https://meownuri-sol-v16-story-preview-2kizo6wd1.vercel.app/

Vercel project prj_ku5e3PV4AQReelBjBZTkxYxVdz0G

Deployment dpl_Ghw5VBFdF2RPhXJJdx8mVirUzhTR / READY, production alias 설정 확인.

소스: GitHub jiakwonau-sudo/Meownuri, branch feat/sol-v16-day01-10-20261011

Google Drive 원본: MEOWNURI/SOL_v16.0_DAY01-10_20261011/MEOWNURI_SOL_v16.1_PLAYABLE_PREVIEW.html



2. CHANGESET

- TITLE 시작 화면에 ‘🏘️ DAY 4–10 바로 플레이’ 버튼 추가, Day 3 저장 완료 없이 새 이야기 체험 가능.

- 실시간 2D/3D 세계 목표를 향해 이동하는 ‘🐾 목표로 걷기’ 버튼 추가. 도착 후 실제 행동 버튼 클릭 필요.

- 📖 챕터 선택 메뉴 Day 4~10. 초반 Day 1~3 게임과 기존 모듈은 그대로 유지.

- 소스는 v16.0 위에 작은 인라인 UI 오버레이를 추가한 v16.1 빌드.

- 무대사 원칙: 캐릭터 대사 새로 추가하지 않음.



3. TEST RESULTS

- 모바일 에뮬레이션 390×844 화면: 타이틀 -> Day4 시작 PASS.

- Day 4~10: 총 33개 모든 비트에 대해 버튼을 실제로 클릭, 자동 걷기로 근접, 필수 선택 UI 실제 클릭, 날짜별 다음 날 전환 PASS; qaAdvance() 사용 안 함.

- Day 9의 세 선택 -> Day 10의 엔딩 A(왕국), B(마을), C(다리) 각각 실제 버튼으로 PASS.

- 종료 후 챕터 재시작 PASS.

- Day4 첫 비트 뒤 저장 후 새 페이지 이어하기: PASS (localStorage shim 사용).

- 모바일 CDP 터치 이벤트로 조이스틱 실제 움직임 6.0m 관찰 PASS.

- Day1 처음 시작 및 조이스틱/점프 버튼 표시 PASS.

- 모든 상기 시험 경로에서 pageerror 0건.

- 제한된 Chromium에서 WebGL 생성 불가 -> 안전 2D 렌더러로 플레이되며 지형·고양이 표시 PASS.

- 공개 HTTPS 파일의 sha256 b1fb2cf3e95795810e50ef96f3a39b283f831d7529333cc8830c7594b089de38 확인.

- GitHub Actions 38104457617 HTTPS/파일 해시/버튼 문자열 검증 SUCCESS.

https://github.com/jiakwonau-sudo/Meownuri/actions/runs/38104457617



4. NOT YET VERIFIED

- 정상 WebGL 3D/GPU 렌더링 및 Android 실기기 성능, 스크린샷.

- Day1 -> Day10 전체를 처음부터 정상 조작만으로 이어가는 자연 플레이.

- Day 4~10의 하루 10~15분 풀 볼륨, 고급 애니메이션·감정 타이밍은 기존 기획보다 간소한 현재 4~6 비트/날.

- 기존 저장파일 모든 조합과 자동 카메라 충돌 테스트.

- 실제 호스팅 접속의 브라우저 클릭 자동화는 외부 샌드박스 제한으로 미완료 (독립적으로 HTTPS 바이트 동일성 검증).

Android에서 실제 화면이 안 뜨거나 동작이 안 되면 런타임 재검증 필요. '완성' 혹은 Production Ready라고 표기하지 않는다.



5. TEST PLAY HOWTO

1) 공개 HTTPS 접속 → '🏘️ DAY 4–10 바로 플레이'.

2) 화면의 목표까지 조이스틱 이동하거나 ‘🐾 목표로 걷기’ 선택.

3) ‘🐾' 동작 버튼 → 다음 비트 진행.

4) Day 5/7/9 선택지 탭, 각 날짜 마지막 '다음 날' 탭.

5) 📖은 날짜 선택 메뉴. 원래 이야기부터 보려면 첫 화면의 '처음부터'.

