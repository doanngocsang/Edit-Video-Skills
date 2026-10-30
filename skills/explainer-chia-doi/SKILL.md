---
name: explainer-chia-doi
description: "Edit video talking-head dọc 9:16 theo phong cách EXPLAINER CHIA ĐÔI: nửa trên là đồ hoạ giải thích (tiêu đề hộp đỏ, icon bật lên, ảnh chụp màn hình cuộn, gõ chữ giả lập, nhãn số liệu, lưới video, thẻ so sánh, sơ đồ nhánh), nửa dưới là khung mặt người nói bo góc, caption từng từ. Kích hoạt khi khách nói 'explainer chia đôi', 'video hướng dẫn chia đôi màn hình', 'video chia sẻ kiến thức có đồ hoạ', 'kiểu video ChatGPT/tutorial', hoặc đưa video nói chuyện kèm ảnh chụp màn hình và muốn minh hoạ từng bước."
---

# Explainer chia đôi

## Sản phẩm là gì
Video talking-head (1 người nói trước camera) → video dọc 9:16 kiểu **video
hướng dẫn / chia sẻ kiến thức**:
- Xen kẽ 2 bố cục: **toàn màn hình** (mặt người, lúc mở đầu/cảm xúc/kết) và
  **chia đôi** (nửa trên đồ hoạ minh hoạ, nửa dưới khung mặt bo góc).
- Mỗi ý có **tiêu đề**: chữ đậm + **từ khoá trong hộp đỏ** + dòng phụ **serif
  nghiêng**.
- Đồ hoạ xuất hiện **đúng lúc người nói nhắc tới** (bám word-timestamps).
- **Caption từng từ** — giữa đồ hoạ và khung mặt (đoạn chia đôi), dưới 1/3
  khung (đoạn toàn màn hình).
Không dùng AI tạo cảnh; toàn bộ là đồ hoạ 2D dựng bằng code.

## Quy ước
- Thư mục gốc dự án = thư mục làm việc hiện tại:
  ```
  input/          ← video nói chuyện của khách
  input/shots/    ← ảnh chụp màn hình, ảnh bìa video, avatar… khách đưa
  work/           ← file trung gian (words.json, plan.json, khung PNG)
  output/         ← thành phẩm
  assets/{fonts,icons}/
  ```
- Script: `scripts/explainer_render.py` (đường dẫn tính từ thư mục skill này).
- Mọi mốc thời gian lấy từ transcript **SAU khi cắt**.

---

## Cài đặt môi trường (làm 1 lần mỗi máy — có rồi thì bỏ qua)
```bash
ffmpeg -version
python --version || python3 --version
```
- **ffmpeg** (cần filter `subtitles`/libass): Windows `winget install Gyan.FFmpeg`
  · macOS `brew install ffmpeg` · Linux `sudo apt install ffmpeg`.
- **Python 3.10+**:
  ```bash
  python -m venv .venv
  # Windows: .venv\Scripts\activate   |   Mac/Linux: source .venv/bin/activate
  pip install faster-whisper playwright pillow
  python -m playwright install chromium
  ```
  Máy đã có các thư viện này trong môi trường khác (vd skill Dạng 1) thì dùng
  lại môi trường đó, không cần cài lại.
- **Kiểm tra**: `python -c "import faster_whisper, playwright, PIL; print('OK')"`

### Lưu ý Windows
- PowerShell 5: luôn gõ `curl.exe` (không phải `curl`).
- Chạy script từ **thư mục gốc dự án** để đường dẫn caption tương đối, tránh
  lỗi escape `C:` trong filter `subtitles`.

## Tài nguyên tự lấy (kiểm `assets/` trước, thiếu mới tải)
- **Font** (TTF, có dấu tiếng Việt), đặt đúng tên file vào `assets/fonts/`:
  - `BeVietnamPro-ExtraBold.ttf` — tiêu đề + caption:
    `curl.exe -L -o assets/fonts/BeVietnamPro-ExtraBold.ttf https://github.com/google/fonts/raw/main/ofl/bevietnampro/BeVietnamPro-ExtraBold.ttf`
  - `Lora-Italic.ttf` — dòng phụ serif nghiêng: tìm file trong
    `https://github.com/google/fonts/tree/main/ofl/lora` (bản italic, thường là
    `Lora-Italic[wght].ttf` → đổi tên thành `Lora-Italic.ttf`).
  - Thiếu font → script vẫn chạy bằng font hệ thống, nhưng nên có đủ.
- **Logo thương hiệu** (TikTok, Facebook, YouTube, Instagram, Google…) — Simple
  Icons (CC0): `curl.exe -L -o assets/icons/tiktok.svg https://unpkg.com/simple-icons/icons/tiktok.svg`
  (slug: `facebook`, `youtube`, `instagram`, `google`…). Không tìm thấy logo
  nào (vd ChatGPT/OpenAI) → hỏi khách file logo, hoặc dùng icon chung Lucide
  (`https://unpkg.com/lucide-static/icons/<ten>.svg`, vd `bot`, `sparkles`).
  SVG Simple Icons là màu đen → khi đặt trên nền đen dùng ô trắng (`icon`
  có sẵn nền trắng) hoặc đặt `sourceBg` trắng trong `flow`.

## Khách phải tự cung cấp
- Video nói chuyện (bắt buộc).
- Ảnh chụp màn hình cho phần minh hoạ (nên có): trang kênh, câu trả lời AI,
  bảng số liệu, ảnh bìa video… đặt trong `input/shots/`. Ảnh dài (chụp cuộn)
  sẽ được cuộn chậm trong khung. Khách đưa **video quay màn hình** → trích 1–2
  khung hình rõ nhất thành ảnh (`ffmpeg -ss <giây> -i rec.mp4 -frames:v 1 input/shots/x.png`).
- Không có ảnh nào → vẫn làm được bằng các phần tử không cần ảnh: tiêu đề,
  icon, gõ chữ, nhãn số liệu, sơ đồ nhánh, chữ to.

---

## Quy trình

### 1. Chuẩn hoá & cắt gọn
- Đưa về **1080×1920, 30fps** (crop giữa nếu video ngang và mặt ở giữa; nếu
  không thì nền mờ + video giữa).
- Transcribe lần 1: faster-whisper, `language="vi"`, `word_timestamps=True`,
  `initial_prompt="Ừm, à, ờ, kiểu như, thì là."` (giữ từ đệm để cắt).
- Cắt gọn: ngưỡng lặng = `mean_volume − 15dB` (kẹp −45…−25dB, đo bằng
  `volumedetect`); chỉ cắt lặng ≥ 0.6s; bỏ từ đệm, câu vấp (giữ lần nói tốt),
  rác đầu/cuối; jump cut dứt khoát, không cắt giữa từ, chừa 0.15s đệm, fade
  âm 15ms mỗi điểm nối. Cắt > 40% thời lượng → dừng, báo khách duyệt.
- Xuất `work/cut.mp4`.

### 2. Transcribe lần 2 → `work/words.json`
Trên `work/cut.mp4`, lưu dạng `[{"word": "...", "start": s, "end": e}, ...]`.

### 3. Lập kịch bản đồ hoạ → `work/plan.json` (bước quan trọng nhất)
Đọc toàn bộ transcript, chia video thành các đoạn:

**Chọn bố cục:**
- `full` (toàn màn hình): 1–3s mở đầu nếu người nói chào/hook cảm xúc, các câu
  chuyển ý ngắn, câu kết/kêu gọi hành động.
- `split` (chia đôi): mỗi khi nói về **bước, công cụ, nền tảng, con số, ví dụ,
  so sánh**. Mục tiêu 60–80% thời lượng là `split`.
- Mỗi đoạn `split` dài 1.5–6s; đổi đoạn/tiêu đề khi người nói sang ý mới.

**Tiêu đề mỗi ý** (`header` hoặc `headers` nếu đổi giữa đoạn):
- `text` (1–3 từ dẫn) + `accent` (từ khoá ≤ 3 từ, nằm trong hộp đỏ) + `sub`
  (cụm serif nghiêng, tuỳ chọn). Ví dụ: "Cách dùng" + **ChatGPT** + *tối ưu
  kênh TikTok*; "Bước 2:" + **Gửi link kênh**.
- Viết lại cho gọn, không chép nguyên câu nói.

**Chọn phần tử minh hoạ theo nội dung câu nói:**
| Người nói đang… | Dùng `type` |
|---|---|
| Nhắc tên công cụ/nền tảng/khái niệm | `icon` (logo bật lên, có thể kèm `label`) |
| Nói về 1 trang/kết quả có ảnh chụp | `screenshot` (khung viền đỏ; `scroll` nếu ảnh dài; `corners` gắn logo ở 2 góc) |
| Hướng dẫn gõ/nhập/hỏi AI | `typing` (ô chat, chữ hiện dần) |
| Đọc con số | `stats` (thẻ đỏ bay vào 2 bên, thường đi cùng `screenshot`) |
| Nói về nhiều video/bài đăng nổi bật | `grid` (lưới ảnh bìa, `highlights` viền đỏ + số view) |
| So sánh 2 bên (mình vs đối thủ, trước vs sau) | `compare` (2 thẻ trượt vào) |
| Nhiều nguồn → 1 công cụ → kết quả | `flow` (3 icon, đường cong tự vẽ, ô kết quả) |
| Câu chốt/1 từ đắt giá | `text` (chữ rất to bật lên) |

**Thời điểm:** `at` = mốc `start` của **từ khoá đầu tiên** trong câu nhắc tới
phần tử đó (lấy từ words.json); `until` = lúc chuyển phần tử khác (bỏ trống =
hết đoạn). Mỗi lúc chỉ 1 phần tử chính (+ `stats` đi kèm được).

**Vị trí (y, px trên khung 1080×1920):** vùng đồ hoạ an toàn y = 330–1080.
Tiêu đề chiếm ~150–320, caption ở 1150, khung mặt từ 1250 trở xuống — không
đặt đồ hoạ đè lên các vùng đó.

**Màu/nền:** `theme: "light"` (nền kem, chữ đen) cho đoạn mở đầu nhẹ nhàng;
`"dark"` (nền đen) cho phần nội dung chính — giữ 1 theme cho cả mạch nội dung,
chỉ đổi khi sang phần lớn. `accent` toàn video mặc định đỏ `#E5322D`, đổi theo
màu thương hiệu khách nếu có.

#### Schema `plan.json`
```json
{
  "accent": "#E5322D",
  "faceY": 0.36,
  "segments": [
    {"start": 0.0, "end": 3.0, "layout": "split", "theme": "light",
     "header": {"text": "Cách dùng", "accent": "ChatGPT", "sub": "tối ưu kênh TikTok"},
     "items": [
       {"type": "icon", "src": "assets/icons/chatgpt.png", "label": "ChatGPT", "at": 0.3, "until": 1.6, "y": 420},
       {"type": "screenshot", "src": "input/shots/profile.png", "at": 1.6, "w": 520, "h": 560, "y": 360,
        "corners": ["assets/icons/tiktok.svg", "assets/icons/facebook.svg"]}
     ]},
    {"start": 3.0, "end": 4.2, "layout": "full"},
    {"start": 4.2, "end": 7.4, "layout": "split", "theme": "dark",
     "headers": [{"at": 4.2, "text": "Bước 1:", "accent": "Truy cập ChatGPT"},
                 {"at": 5.6, "text": "Bước 2:", "accent": "Gửi link kênh"}],
     "items": [{"type": "typing", "text": "phân tích kênh tiktok này: https://...", "at": 5.8, "y": 520, "cps": 18}]}
  ]
}
```
Tham số từng `type` (ngoài `at`, `until`, `y`):
- `icon`: `src`, `label`.
- `screenshot`: `src`, `w` (620), `h` (620, chiều cao khung nhìn), `scroll`
  (0–1, tỉ lệ phần ảnh dư được cuộn), `scrollDelay` (0.8s), `corners` (≤ 2 logo).
- `typing`: `text`, `cps` (ký tự/giây, 18), `delay` (0.3s).
- `stats`: `stats: [{value, label, side: left|right, y, x}]`, `stagger` (0.3s).
- `grid`: `images` (danh sách ảnh), `cols` (6), `highlights: [{i, label}]`, `hlDelay`.
- `compare`: `cards: [{title, tag, ok, img, rival: true|false}]`, `cardAt` (mốc vào từng thẻ).
- `flow`: `sources` (3 logo), `center` (logo giữa), `result` (chữ ô kết quả), `sourceBg`.
- `text`: `text`.
- Đoạn: `noCaption: true` để tắt caption riêng đoạn đó.
- `faceY` (0–1): tâm khung mặt theo chiều dọc video gốc — xem 1 khung hình để
  chỉnh cho mặt + vai nằm gọn trong khung bo góc.

### 4. Dựng
Chạy từ thư mục gốc dự án:
```bash
python <skill>/scripts/explainer_render.py --video work/cut.mp4 --plan work/plan.json \
       --words work/words.json --out output/<tên-video>-explainer.mp4
```
- Chỉ xem thử đồ hoạ trước khi ghép: thêm `--only-frames` → xem PNG trong
  `work/explainer/segXX/`.
- Font caption khác: `--caption-font "Tên font"` (tên family trong file TTF).
- Script tự: lấp khoảng trống giữa các đoạn bằng `full`, căn mốc theo khung
  30fps, render đồ hoạ, cắt khung mặt bo góc, đốt caption từng từ (màu tự đổi
  theo nền), giữ audio gốc + chuẩn hoá −14 LUFS, xuất H.264.

### 5. Kiểm tra trước khi giao (bắt buộc)
- `ffprobe`: 1080×1920, có audio, thời lượng ≈ `cut.mp4`.
- Trích 1 khung giữa mỗi đoạn `split` + 2 khung `full` → XEM từng ảnh:
  tiêu đề không tràn/không bị cắt dấu, đồ hoạ không đè caption/khung mặt,
  mặt nằm gọn trong khung, ảnh chụp đọc được, phần tử xuất hiện đúng lúc nói.
- Lỗi → sửa `plan.json` rồi chạy lại (nhanh), không giao bản lỗi.
- Báo khách: đường dẫn file, số đoạn chia đôi / toàn màn hình, danh sách tiêu đề.

---

## Gọi từng hiệu ứng (khách ra lệnh bằng tên)
"edit explainer chia đôi" = Agent tự lập kịch bản theo luật ở bước 3. Khách
có thể gọi/chỉnh riêng — lệnh khách thắng luật tự động:

| Tên gọi | Hiệu ứng | Nói kèm được |
|---|---|---|
| **"chia đôi"** / **"toàn màn hình"** | Bố cục đoạn | "giây 5–9 chia đôi", "đoạn kết toàn màn hình" |
| **"tiêu đề hộp đỏ"** | `header` | "tiêu đề: Bước 1 / Truy cập ChatGPT", "dòng phụ: …", "màu hộp xanh" |
| **"icon bật lên"** | `icon` | "logo TikTok ở giây 4" |
| **"ảnh chụp cuộn"** | `screenshot` | "dùng ảnh chat.png", "cuộn hết", "không cuộn", "gắn logo 2 góc" |
| **"gõ chữ"** | `typing` | "gõ: …", "gõ nhanh/chậm" |
| **"nhãn số liệu"** | `stats` | "47.8K followers bên trái, 1.9M view bên phải" |
| **"lưới video"** | `grid` | "đánh dấu 3 video đầu, số view …" |
| **"thẻ so sánh"** | `compare` | "Kênh của bạn vs Đối thủ" |
| **"sơ đồ nhánh"** | `flow` | "TikTok, Facebook, YouTube → ChatGPT → Báo cáo" |
| **"chữ to"** | `text` | "chữ to 'MIỄN PHÍ' ở giây 20" |
| **"caption"** | Caption từng từ | "tắt caption đoạn …" |
| **"nền sáng"** / **"nền tối"** | `theme` | "cả video nền tối" |

Ví dụ lệnh: *"edit explainer chia đôi, nền tối, đoạn 0–3s toàn màn hình, giây
8 dùng ảnh chat.png cuộn hết kèm nhãn 47.8K followers"*.

## Khách chỉ cần làm gì
1. Video vào `input/`, ảnh chụp màn hình vào `input/shots/`.
2. Nói: *"edit explainer chia đôi cho video này"*.

Agent tự: kiểm môi trường → tải font/logo thiếu → chuẩn hoá & cắt gọn →
transcribe lại → lập `plan.json` → dựng → kiểm tra khung hình → báo đường dẫn
`output/<tên-video>-explainer.mp4`.
