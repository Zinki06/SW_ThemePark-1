### 📌 `gpt-image-1`

| 항목 | 핵심 정보 |
|---|---|
| **모델 ID** | `gpt-image-1` |
| **엔드포인트** | `POST https://api.openai.com/v1/images/generations` (생성)<br>`POST …/images/edits`, `…/images/variations` (편집/변형) |
| **필수 파라미터** | `model`, `prompt`, `n`, `size`  (`1024×1024`, `1152×896`, `1536×1024` 등)<br>선택: `style`, `quality`, `response_format`(`url` / `b64_json`), `moderation`(`auto`/`low`)  ([Introducing our latest image generation model in the API | OpenAI](https://openai.com/index/image-generation-api/)) |
| **입 / 출력 형식** | 텍스트(프롬프트)·이미지 입력 → 이미지 URL 또는 Base-64 출력 |
| **가격** | *텍스트 입력* $5 / 1M tokens<br>*이미지 입력* $10 / 1M tokens<br>*이미지 출력* $40 / 1M tokens (대략 1장당 $0.02 ~ $0.19)  ([Introducing our latest image generation model in the API | OpenAI](https://openai.com/index/image-generation-api/)) |
| **cURL 예시** | ```bash
curl https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-1",
    "prompt": "a futuristic city at sunset, wide angle",
    "n": 1,
    "size": "1024x1024",
    "response_format": "url"
  }'```  ([Generate Image | OpenAI API - Postman](https://www.postman.com/devrel/openai/request/riub8s3/generate-image?utm_source=chatgpt.com)) |

---

### 📌 `gpt-4o` (및 `gpt-4o-mini`)

| 항목 | 핵심 정보 |
|---|---|
| **모델 ID** | `gpt-4o`  /  `gpt-4o-mini` (텍스트·비전)<br>`gpt-4o-realtime-preview`  /  `gpt-4o-mini-realtime-preview` (실시간 음성·오디오) |
| **엔드포인트** | `POST https://api.openai.com/v1/chat/completions` (텍스트·비전)<br>`POST …/audio/realtime` (실시간 음성) |
| **필수 파라미터** | `model`, `messages` (role + content)<br>선택: `max_tokens`, `temperature`, `tools`, `json_mode`, `vision`·`audio` 입력 등 |
| **컨텍스트** | 최대 128 k tokens 입력 가능  ([How to access and use GPT-4o's API, step by step - Benjamin Crozat](https://benjamincrozat.com/gpt-4o?utm_source=chatgpt.com)) |
| **가격** | *입력* $5 / 1M tokens *출력* $15 / 1M tokens  ([ChatGPT4o API Pricing for Input and Output - API - OpenAI Developer Community](https://community.openai.com/t/chatgpt4o-api-pricing-for-input-and-output/746258)) |
| **cURL 예시** | ```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role":"system","content":"You are an assistant."},
      {"role":"user","content":"Hello!"}
    ]
  }'```  ([How to access and use GPT-4o's API, step by step - Benjamin Crozat](https://benjamincrozat.com/gpt-4o?utm_source=chatgpt.com)) |

---


