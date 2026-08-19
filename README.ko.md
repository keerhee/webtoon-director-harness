# 웹툰 디렉터 하네스 (Webtoon Director Harness)

[English](README.md) · **한국어**

[![CI](https://github.com/keerhee/webtoon-director-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/keerhee/webtoon-director-harness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

웹툰·만화 제작을 위한 **감독실(Director's Room)** 하네스. 상위의 콘티 단계와 하위의 작화/제작
단계 **사이**에서 동작하며, 개선하는 대상은 그림이나 문장이 아니라 **연출** — 독자가 무엇을
이해하고, 무엇을 느끼며, 무엇을 어떤 순서로 보게 되는가 — 입니다.

> 클린룸 스캐폴드입니다. 서드파티 스킬 파일·프롬프트·에셋을 이 저장소에 복제하지 않으며,
> 연동은 문서화된 파일 입출력으로만 이루어집니다. [NOTICE.md](NOTICE.md) 참고.

## 왜 필요한가

한 번의 생성 패스는 너무 일찍 수렴합니다. 장면 연출을 시키면 모델은 *변호 가능한* 첫 번째
화면 구성 — 무난하고, 평범하며, 결코 세 번째 아이디어는 아닌 것 — 을 내놓습니다. 그리고 그
결과를 스스로 리뷰하는데, 자기 리뷰는 결과가 아니라 노력을 채점합니다.

연출의 실패는 문장 품질 검사로는 보이지 않는 방식으로 일어납니다. 한 컷 일찍 도착한 리빌,
빠져버린 리액션 컷, 폰에서 평평해지는 스크롤, 아직 듣지 못한 정보를 근거로 행동하는 캐릭터.
이 저장소는 **생성 · 전문화 · 비평 · 종합 · 검증**을 서로 다른 에이전트로 분리하고, 이들이
오직 파일을 통해서만 소통하게 만듭니다.

**핵심 원칙: 첫 번째로 그럴듯한 연출안을 그대로 채택하지 않는다.**

## 워크플로

```text
상위 콘티 / Stage 1
        │
        ▼
  입력 정규화 ──▶ 내러티브 분석
                        │
        ┌───────────────┼───────────────┐
   Emotional        Cinematic      Webtoon-native      ← 독립 팬아웃
        └───────────────┼───────────────┘
                        ▼
              멀티 크리틱 리뷰          ← 후보별 1회, 선호도를 모른 채 근거 기반 채점
                        ▼
              디렉터 종합(synthesis)    ← 척추 + 이식(graft) + 결정 로그
                        ▼
              대사·침묵 패스
                        ▼
        연속성 + 품질 게이트 ──실패──▶ 제한된 수정 루프
                        │ 통과
                        ▼
          제작 인계 / Stage 2
```

자세한 내용: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/WORKFLOW.md](docs/WORKFLOW.md)

## 에이전트

| 에이전트 | 담당 |
|---|---|
| **Showrunner** | 최종 창작 결정권, 이해충돌 조정, 종합 |
| **Narrative Director** | 장면 목표, 드라마틱 비트, 리빌 순서, 훅 |
| **Cinematography Director** | 샷·앵글·구도·깊이·조명·시각적 리빌 |
| **Emotion Director** | 감정 비트, 리액션, 침묵, 기대감 |
| **Pacing Director** | 컷 타이밍, 스크롤 리듬, 여백, 패널 높이 |
| **Dialogue & Silence Editor** | 압축, 서브텍스트, 말풍선 순서, SFX, 침묵 |
| **Continuity Supervisor** | 인물·소품·공간·조명·시간선·지식 상태 |
| **Direction Critic** | 6축 근거 기반 채점, 수정 요청 |

역할 매트릭스와 설계 근거: [docs/AGENTS.md](docs/AGENTS.md)

## 빠른 시작

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

python scripts/init_episode.py ep01
```

상위 인계서와 레이아웃 파일을 `_workspace/ep01/00_input/`에 넣은 뒤, Claude Code에서:

```text
이 프로젝트의 Director's Room을 실행해줘.
_workspace/ep01/00_input을 읽고 Emotional / Cinematic / Webtoon-native
세 연출안을 병렬 생성한 뒤 multi-critic review와 synthesis를 수행하고,
quality gate를 통과할 때까지 수정한 후 06_handoff에 최종 산출물을 만들어줘.
```

목표 품질을 먼저 확인하려면 워크드 예제로 에피소드를 시드할 수 있습니다.

```bash
python scripts/init_episode.py demo --from-example
```

## 워크드 예제

[`examples/sample_episode/`](examples/sample_episode)는 7컷 장면에 대한 **전 단계 완주 기록**입니다.
서로 실제로 갈라지는 세 개의 후보안, 세 번의 독립 리뷰(7.60 / 7.85 / 8.20 — 전부 `revise`),
세 후보에서 각각 이식해 **8.85**를 받은 종합안, 연속성 검증, 그리고 최종 인계 패키지가 들어
있습니다. [`06_handoff/direction_bible.md`](examples/sample_episode/06_handoff/direction_bible.md)와
[`04_synthesis/decision_log.md`](examples/sample_episode/04_synthesis/decision_log.md)부터 읽어 보세요.

## 입력과 출력

```text
_workspace/<episode>/
  00_input/       normalized_input.yaml, source_handoff.md, layouts/
  01_analysis/    narrative_analysis.yaml
  02_candidates/  emotional.yaml · cinematic.yaml · webtoon_native.yaml
  03_reviews/     critic_<candidate>.yaml · quality_gate_result.yaml
  04_synthesis/   selected_direction.yaml · decision_log.md · dialogue_pass.yaml
  05_continuity/  continuity_state.yaml · continuity_report.yaml
  06_handoff/     direction_bible.md · panel_direction.yaml · continuity_state.yaml
                  critic_report.md · stage2_handoff.md
```

인계 산출물은 **제작 중립적**입니다. 특정 이미지 모델·작화 도구·스튜디오 파이프라인을 전제하지
않으므로, 같은 인계서로 서로 다른 제작 단계를 구동할 수 있습니다.

## 품질 게이트

| 평가 축 | 가중치 |
|---|---:|
| 내러티브 명료성 (narrative clarity) | 20% |
| 감정 임팩트 (emotional impact) | 20% |
| 시각 구성 (visual composition) | 20% |
| 페이싱·스크롤 (pacing / scroll) | 15% |
| 연속성 (continuity) | 15% |
| 가독 흐름 (reading flow) | 10% |

통과 기준 **8.5 / 10**, 수정 루프 최대 3회. 9점 이상에는 **패널 단위 근거가 반드시 필요**하며,
하드페일(연속성 붕괴, 말풍선 순서 불가독, 캐릭터 동일성 불일치, 클라이맥스·리빌 부재)이 하나라도
있으면 총점과 무관하게 수정으로 넘어갑니다. [docs/SCORING.md](docs/SCORING.md) ·
[`config/quality_gate.yaml`](config/quality_gate.yaml)

```bash
python scripts/score_direction.py _workspace/ep01/03_reviews/critic_*.yaml
python scripts/validate_artifacts.py _workspace/ep01     # 스키마 + 어휘 + 패널 ID
python scripts/validate_handoff.py _workspace/ep01/06_handoff
pytest
```

### 예제의 실제 점수

| 후보 | 명료성 | 감정 | 구성 | 페이싱 | 가독 | 연속성 | 가중 총점 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| emotional | 8 | 9 | 7 | 7 | 8 | 8 | **7.85** | revise |
| cinematic | 9 | 7 | 9 | 7 | 8 | 9 | **8.20** | revise |
| webtoon_native | 7 | 8 | 7 | 9 | 8 | 7 | **7.60** | revise |
| synthesis | 9 | 9 | 9 | 8 | 9 | 9 | **8.85** | pass |

종합안이 모든 후보를 상회하는 것이 이 구조가 의도한 결과입니다. 종합안이 최고 후보보다 낮게
나온다면, Showrunner가 선택·이식이 아니라 평균을 낸 것입니다.

## 연출 언어

샷·앵글·트랜지션·비트 지속·드라마틱 기능은
[`config/direction_vocabulary.yaml`](config/direction_vocabulary.yaml)의 통제 어휘에서 가져오며,
패널 스키마와 검증 스크립트가 이를 강제합니다. 자유 서술 용어는 채점·비교·작화를 모두
불가능하게 만들기 때문입니다. 레퍼런스: [docs/DIRECTION_LANGUAGE.md](docs/DIRECTION_LANGUAGE.md)

`purpose`(연출 의도) 한 줄은 모든 패널의 필수 항목이며, 리뷰어가 가장 먼저 읽는 필드입니다.

| 약한 예 | 강한 예 |
|---|---|
| "극적인 로우 앵글." | "로우 앵글로 그녀 뒤의 알코브를 화면에 남긴다 — 그녀가 한눈판 사이에도 다음 위협이 계속 존재한다." |
| "구도가 좋다." | "버즈아이로 공간의 깊이를 없애 방 전체를 증거 하나로 축약한다." |
| "감정을 보여준다." | "멈춘 손만 남기고 잘라내 독자가 표정을 스스로 채우게 한다." |

선택의 이유가 "보기 좋아서"뿐이라면, 그 선택을 버리거나 이유를 찾아야 합니다.

## 저장소 구조

```text
.claude/          에이전트 8종 + 스킬 4종 + 프로젝트 지침 (창작 코어)
harness/          채점·설정 로딩·아티팩트 검증 (결정론적 코어)
config/           품질 게이트, 연출 모드, 통제 어휘
schemas/          모든 구조화 산출물의 JSON Schema
scripts/          init_episode · score_direction · validate_artifacts · validate_handoff
templates/        디렉션 바이블 · 크리틱 리포트 · Stage 2 인계서
docs/             아키텍처 · 워크플로 · 채점 · 에이전트 · 연출 언어
examples/         CI에서 검증되는 완주 예제 에피소드
adapters/         상위 도구와의 파일 기반 연동 문서
tests/            구조 · 프롬프트 · 스키마 · 채점 · 예제 정합성 테스트
```

## 기여

[CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요. 이 저장소는 상당 부분이 프롬프트와 계약이므로,
`.claude/` 변경은 `harness/` 변경과 동등하게 다뤄집니다. 어휘를 추가할 때는 어휘 파일·스키마
enum·문서를 함께 고쳐야 하며, 일부만 바꾸면 CI가 실패합니다.

## 라이선스

MIT — [LICENSE](LICENSE) 참고. 서드파티 연동 조건은 [NOTICE.md](NOTICE.md)를 확인하세요.
