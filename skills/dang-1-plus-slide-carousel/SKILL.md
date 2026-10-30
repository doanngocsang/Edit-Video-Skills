---
name: dang-1-plus-slide-carousel
description: "Bản nâng cấp của 'Dạng 1' — edit video nói chuyện (talking-head) dọc 9:16: cắt gọn tự nhiên + title hook hộp trắng + caption động + CAROUSEL 3D (các thẻ video xoay vòng quanh người nói) + thẻ liệt kê + chữ trượt. Kích hoạt khi khách nói 'edit Dạng 1 plus', 'Dạng 1 có carousel', 'thẻ video xoay quanh người', 'video bay vòng quanh', hoặc đưa clip nói chuyện kèm vài clip B-roll và muốn hiệu ứng carousel. Nếu khách chỉ muốn bản sạch không hiệu ứng thì dùng 'dang-1-thoai-thumbnail'."
---

# Dạng 1 Plus — Thoại + Thumbnail + Slide/Carousel

## Sản phẩm là gì
1 người nói chuyện trước camera → video ngắn dọc 9:16:
- cắt gọn tự nhiên (jump cut, bỏ khoảng lặng/từ đệm/vấp),
- mở đầu bằng **thumbnail** do AI viết, **trượt ra** để lộ video,
- **caption động** chạy theo lời nói,
- **carousel 3D**: các thẻ video xoay vòng quanh người nói (thẻ sau bị người
  che, thẻ trước đè lên người, vòng sáng quỹ đạo) — ở hook và các câu nói về
  "nhiều video/nhiều cảnh",
- **title hook hộp trắng** (dòng nhấn chữ đen trong hộp trắng),
- **thẻ liệt kê phẳng** khi người nói liệt kê ý ("3 bước", "thứ nhất…"),
- **slide** nhẹ cho các phần tử chữ (vào/ra bằng chuyển động trượt, không dissolve).

So với Dạng 1 gốc: thêm carousel 3D + title hộp trắng + slide + thẻ liệt kê.
Vẫn KHÔNG có: zoom nhịp cảm xúc, crop bám mặt đổi hình, sản phẩm 3D/AI tạo
cảnh, infographic số liệu (đó là Dạng 2/3/4).

## Quy ước chung
- **Thư mục gốc dự án** = thư mục làm việc hiện tại của agent. Trong đó có:
  ```
  input/     ← video khách đưa
  work/      ← file trung gian (transcript, đoạn cắt, overlay PNG, .ass)
  output/    ← thành phẩm
  assets/{fonts,icons,sfx,music}/
  ```
  Chưa có thì tự tạo.
- Ngôn ngữ transcribe: cố định `vi` (đừng để auto).
- Mọi mốc thời gian cho thumbnail/caption/carousel lấy từ **transcript SAU
  khi cắt**, không lấy bản gốc.

---

## Cài đặt môi trường (làm 1 lần mỗi máy)

Tự kiểm tra và tự cài. Chỉ dừng lại hỏi khách khi môi trường chặn quyền cài.

```bash
ffmpeg -version
python --version || python3 --version
node --version
```

1. **ffmpeg** (bắt buộc, phải có libass để đốt caption `.ass`):
   Windows `winget install Gyan.FFmpeg` · macOS `brew install ffmpeg` ·
   Linux `sudo apt install ffmpeg`. Kiểm `ffmpeg -filters | grep subtitles`
   (Windows: `findstr subtitles`).
2. **Python 3.10+** — CHỈ cần đúng thứ Dạng 1 Plus dùng:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate   |   Mac/Linux: source .venv/bin/activate
   pip install faster-whisper playwright mediapipe opencv-python numpy
   python -m playwright install chromium
   ```
   `mediapipe` + `opencv` dùng để tách người cho carousel 3D (dùng MediaPipe
   Tasks — bản mới đã bỏ `mp.solutions`). Không cần `librosa`. Không GPU →
   Whisper `small`/`medium` chạy CPU là đủ cho video ngắn.
   Script đi kèm: `scripts/orbit_carousel.py`, `scripts/person_matte.py`
   (đường dẫn tính từ thư mục skill này).
3. **Engine dựng chữ động** — chọn theo thứ tự:
   - **A. Skill `hyperframes`** nếu có trong danh sách skill → dùng nó (xem
     `hyperframes-animation`, chạy `hyperframes doctor` qua `hyperframes-cli`).
   - **B. Dự phòng (luôn chạy được):** overlay HTML render bằng Playwright ra
     PNG trong suốt + caption `.ass` + ghép bằng ffmpeg `overlay`. Toàn bộ
     skill này viết sao cho cách B đủ để ra thành phẩm.
4. **Xác nhận xong** (3 lệnh không lỗi mới bắt đầu dựng):
   ```bash
   ffmpeg -version
   python -c "import faster_whisper, playwright, mediapipe, cv2; print('OK')"
   node --version   # chỉ bắt buộc nếu dùng cách A
   ```

### Lưu ý Windows
- PowerShell 5: `curl` là alias của `Invoke-WebRequest` → luôn gõ `curl.exe`.
- Filter `subtitles` cần escape ổ đĩa: `subtitles='C\:/du-an/work/cap.ass'`
  (dùng `/`, escape `:`). Đơn giản nhất: `cd` vào thư mục dự án rồi dùng
  đường dẫn tương đối `subtitles=work/cap.ass:fontsdir=assets/fonts`.

---

## Quy trình

### 1. Chuẩn hoá khung hình 9:16
`ffprobe` lấy kích thước. Trích 1 khung giữa video ra ảnh và XEM nó để quyết:
- Đã dọc 9:16 → scale về 1080×1920.
- Ngang (16:9) và mặt người nằm gần giữa → **crop giữa**:
  `crop=ih*9/16:ih,scale=1080:1920`.
- Ngang và mặt lệch / có 2 người / cần giữ bối cảnh → **nền mờ + video giữa**:
  `split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2`
- Không đổi khung theo thời gian (đó là Dạng 2).

### 2. Transcribe lần 1 (để tìm chỗ cắt)
faster-whisper, `language="vi"`, `word_timestamps=True`,
`vad_filter=False` (để thấy khoảng lặng thật),
`initial_prompt="Ừm, à, ờ, ơ, kiểu như, thì là, nói chung là."` — câu mồi
này giúp Whisper GIỮ từ đệm trong transcript (mặc định nó hay tự bỏ, làm sót
từ đệm khi cắt). Lưu `work/transcript_raw.json`.

### 3. Cắt gọn tự nhiên
- **Ngưỡng lặng theo từng video**, không cố định:
  `ffmpeg -i in.mp4 -af volumedetect -f null -` → lấy `mean_volume` (M).
  `noise = M - 15 dB`, kẹp trong [-45, -25] dB. Rồi
  `silencedetect=noise=<noise>dB:d=0.4`.
- Chỉ cắt khoảng lặng **≥ 0.6s** (0.4–0.6s là nhịp thở, cắt vào lộ).
- Cắt từ đệm ("ừm", "à", "ờ", "kiểu như" khi vô nghĩa), câu nói lại/vấp (giữ
  lần nói tốt nhất — thường là lần sau), rác đầu/cuối ("ok quay nhé", đếm ngược).
- Khe giữa 2 từ có tiếng nhưng transcript trống, dài ≥ 0.3s → nghi từ đệm bị
  Whisper bỏ → cắt.
- Luật: jump cut dứt khoát; cắt tại điểm hết ý, không giữa từ; 2 điểm cắt
  cách < 0.4s thì gộp; chừa ≥ 0.15s đệm trước/sau lời.
- **Giới hạn an toàn:** tổng thời lượng bị cắt > 40% video gốc → dừng, báo
  khách danh sách đoạn định cắt để duyệt, không tự xuất.
- **Chống tiếng "tách":** mỗi đoạn giữ lại thêm `afade` vào/ra 15ms trước khi
  nối (`concat`).
- Xuất `work/cut.mp4`.

### 4. Transcribe lần 2 (trên video ĐÃ cắt)
Như bước 2 nhưng `initial_prompt` bỏ đi (không cần mồi từ đệm nữa). Đây là
nguồn thời gian duy nhất cho các bước sau → `work/transcript.json`.

### 5. Viết thumbnail mở đầu
Đọc toàn bộ transcript, chọn 1 trong 6 bố cục theo tông video:
`stack_hierarchy` (bán hàng/tuyên bố mạnh, chữ xếp tầng) · `magazine` (series,
tiêu đề gọn + số tập) · `serif_mix` (câu hỏi/chia sẻ, serif nghiêng) ·
`lifestyle` (vlog, chữ thường thân thiện) · `brand_word` (1 từ thương hiệu lớn
+ phụ đề nhỏ) · `spaced_caps` (studio/agency, in hoa giãn cách) ·
`hook_box` (**mặc định khi có carousel 3D**): title 2 dòng ở ~1/6 trên khung,
dòng 1 chữ trắng đậm có bóng, dòng 2 (= `accent`) chữ đen đậm trong **hộp
trắng bo góc 12px**; KHÔNG làm tối video, title nằm trên video đang chạy và
ở lại suốt đoạn carousel đầu (không trượt ra ở 2.5s).
- `title`: 4–9 từ, viết lại cho tò mò, KHÔNG copy câu chào.
- `accent`: 1 cụm **nằm nguyên văn trong title** → kiểm bằng code
  (`accent in title`), sai thì viết lại.
- **Cách hiện:** thumbnail **phủ lên** 2.5s đầu của video (không chèn thêm
  thời lượng, audio chạy bình thường). Nền thumbnail = khung video làm tối
  (overlay đen 55%) + chữ. Tại 2.5s thumbnail **trượt lên ra khỏi khung**
  trong 0.35s (xem mục Slide). **Caption ẩn trong lúc thumbnail hiện.**

### 6. Caption động
- Chữ trắng dày (Be Vietnam Pro ExtraBold), viền đen 4–6px hoặc bóng mềm.
- Mỗi lần hiện **2–4 tiếng** (Whisper tách tiếng Việt theo âm tiết), ngắt ở
  ranh giới cụm nghĩa, không tách "điện / thoại".
- Đồng bộ theo word-timestamps; tô màu nhấn (vàng) tiếng đang được nói.
- Vị trí: tâm dọc ~72% chiều cao (dưới 1/3 khung), không che mặt.
- `line-height` ≥ 1.25 / lề trên đủ để dấu chồng (Ẩ, Ữ, Ỗ) không bị cắt.
- Cách B: sinh file `.ass` (PlayResX 1080, PlayResY 1920, Alignment 2,
  MarginV ≈ 500), chữ vào bằng `\move` trượt lên 20px + `\fad(80,0)` 120ms.
- Khi carousel đang hiện, caption vẫn giữ vị trí cũ (carousel ở phía trên).

### 7. SLIDE — chuyển động trượt (chữ/thẻ/thumbnail)
Nguyên tắc: mọi phần tử chữ vào/ra bằng trượt, **ease-out cubic**, 0.3–0.4s;
không dissolve, không xoay, không nảy quá đà.
- Thumbnail ra: trượt lên (y: 0 → -H).
- Thẻ carousel vào: từ phải sang; thẻ cũ ra: sang trái (xem mục 8).
- Video chính KHÔNG có slide transition giữa các jump cut (giữ cắt dứt khoát).

Biểu thức ffmpeg (cách B) cho 1 overlay PNG trượt vào từ phải, dừng ở X0:
```
p = min(1, max(0, (t-T0)/D))
x = X0 + (W - X0) * pow(1-p, 3)
overlay=x='X0+(W-X0)*pow(1-min(1,max(0,(t-T0)/D)),3)':y=Y0:enable='between(t,T0,T1)'
```
Trượt ra sang trái (từ T1-D đến T1): `x = X0 - (X0 + w) * pow(min(1,max(0,(t-(T1-D))/D)),3)`
(ease-in khi ra). Thumbnail trượt lên: đổi trục sang `y` tương tự.

### 8. CAROUSEL 3D — thẻ video xoay vòng quanh người (hiệu ứng chính)
Hình mẫu: 3–6 thẻ video bo góc viền trắng xoay quanh người nói ở **tầm
ngực**, thẻ phía sau bị người che, thẻ phía trước đè lên người, thẻ gần
camera nhất có **viền phát sáng cam**, có **vòng sáng quỹ đạo** dưới chân thẻ.

**Khi nào dùng:** đoạn hook mở đầu (thường 0–5s) và những câu nói về "nhiều
video / nhiều kiểu / nhiều cảnh" — ví dụ "toàn bộ video này…", "mình có thể
làm…", "như là một…". Tối đa 3 lần/video, mỗi lần 3–5s.

**Nội dung trong thẻ:** clip B-roll khách đưa ở `input/broll/` (ưu tiên),
hoặc các đoạn KHÁC trong chính video (cảnh khác/trang phục khác). Thiếu clip
→ dùng ảnh tĩnh; chỉ có 1 clip duy nhất → bỏ hiệu ứng này, không lặp 1 cảnh.

**Dựng (đã có script, chạy được ngay):**
```bash
# 1) tách người trong đúng đoạn T0..T0+D (model MediaPipe tự tải lần đầu)
python scripts/person_matte.py --video work/cut.mp4 --start T0 --duration D --out work/matte1
# 2) render lớp thẻ sau/trước (PNG trong suốt 1080x1920)
python scripts/orbit_carousel.py --cards input/broll/a.mp4 input/broll/b.mp4 input/broll/c.mp4 input/broll/d.mp4 \
       --duration D --out work/orbit1
# 3) ghép: video -> thẻ sau -> người -> thẻ trước (dịch các lớp tới T0)
ffmpeg -i work/cut.mp4 \
  -itsoffset T0 -framerate 30 -i work/orbit1/back/%04d.png \
  -itsoffset T0 -framerate 30 -i work/matte1/%04d.png \
  -itsoffset T0 -framerate 30 -i work/orbit1/front/%04d.png \
  -filter_complex "[0][1]overlay=eof_action=pass[a];[a][2]overlay=eof_action=pass[b];[b][3]overlay=eof_action=pass" \
  -c:a copy work/cut_orbit.mp4
```
Chỉnh theo khung hình thật: `--center-y` = tầm ngực người nói (mặc định
1120), `--radius` (470), `--speed` (40°/s), `--glow` màu viền sáng, `--tilt`
độ nghiêng vòng. Thẻ đi ngang mặt (người đứng thấp) → `--face-clear 0.4`.
`cut.mp4` phải là 30fps 1080×1920 (bước 1) để khung khớp nhau.
Kiểm tra: trích 3 khung trong đoạn → mép người không viền nền, thẻ sau thật
sự nằm sau người, thẻ không che mặt.

### 8b. Thẻ liệt kê (phẳng) — khi nói "3 bước / 5 mẹo"
**Khi nào dùng:** chỉ khi transcript có liệt kê rõ ràng — "3 bước/5 mẹo/…",
"thứ nhất… thứ hai…", "một là… hai là…", "đầu tiên… tiếp theo… cuối cùng".
Không có liệt kê → bỏ qua (đừng ép).

**Cách làm:**
1. Tìm cụm liệt kê; mỗi ý = 1 thẻ. Tối đa 5 thẻ/carousel, tối đa 2 carousel/video.
2. Mỗi thẻ: số thứ tự lớn + nội dung tóm ≤ 6 từ (viết lại, không chép nguyên
   câu dài). Tuỳ chọn 1 icon Lucide hợp nghĩa.
3. Thời gian: thẻ i vào tại mốc **tiếng đầu tiên của ý i** (vd "thứ hai"),
   ở lại đến khi ý i+1 bắt đầu; thẻ cuối ở lại đến hết câu của ý cuối + 0.5s.
4. Chuyển thẻ: thẻ cũ trượt trái ra đồng thời thẻ mới trượt phải vào (0.35s).
   Có hàng **chấm chỉ báo** (●○○) dưới thẻ, chấm hiện tại sáng.
5. Bố cục: thẻ rộng ~880px, góc bo 32px, nền trắng 92% hoặc màu thương hiệu,
   chữ đậm tối màu; đặt ở **1/4 trên** khung (tâm y ≈ 330px) để không che mặt
   và không đụng caption. Xem khung hình thật — mặt người ở cao thì hạ độ mờ
   thẻ hoặc thu nhỏ thẻ còn ~720px.
6. Có SFX "whoosh" nhẹ (≤ -18 dB) khi chuyển thẻ — chỉ khi có file free-license
   trong `assets/sfx/`, không có thì bỏ qua, không bắt buộc.

**Dựng (cách B):** viết 1 file HTML/CSS cho mỗi thẻ (và thumbnail) kích thước
1080×1920 nền trong suốt → Playwright chụp `omit_background=True` ra PNG →
ffmpeg overlay với biểu thức ở mục 7. Font nạp qua `@font-face` từ
`assets/fonts/`.

### 9. Ghép & xuất
Thứ tự lớp (dưới → trên): video đã cắt (đã ghép carousel 3D ở bước 8 →
`work/cut_orbit.mp4`) → thẻ liệt kê → caption → title/thumbnail.
```
-c:v libx264 -preset veryfast -crf 20 -r 30 -pix_fmt yuv420p
-c:a aac -b:a 192k -af loudnorm=I=-14:TP=-1:LRA=11
-movflags +faststart
```
1080×1920 (hoặc tỉ lệ khách yêu cầu). Audio gốc, không nhạc nền trừ khi khách
muốn; nếu có nhạc: nhạc ≤ -20 dB dưới giọng, dùng `sidechaincompress` để nhạc
tự nhỏ khi có lời.
Tên file: `output/<tên-video>-dang1plus.mp4`.

### 10. Kiểm tra trước khi giao (bắt buộc)
- `ffprobe`: đúng 1080×1920, có audio, thời lượng hợp lý so với bản cắt.
- Trích khung tại: 1.0s (thumbnail), 3.0s (sau khi thumbnail ra), giữa mỗi
  thẻ carousel, 1s trước cuối → XEM từng ảnh: chữ không bị cắt dấu, không che
  mặt, carousel không đè caption, `accent` được tô đúng.
- Xem nhanh 3 điểm caption ngẫu nhiên: chữ khớp lời (sai lệch < 0.15s).
- Có lỗi → sửa rồi xuất lại, không giao bản lỗi.
- Báo khách: đường dẫn file, thời lượng trước/sau cắt, title thumbnail, số
  carousel đã thêm.

---

## Gọi từng hiệu ứng (khách ra lệnh bằng tên)
Mặc định "edit Dạng 1 plus" = bật hết theo luật tự động ở trên. Khách có thể
gọi riêng từng hiệu ứng bằng tên dưới đây — làm ĐÚNG phần được gọi, giữ
nguyên phần còn lại; lệnh của khách thắng luật tự động.

| Tên gọi (khách nói) | Hiệu ứng | Tham số khách có thể nói kèm |
|---|---|---|
| **"cắt gọn"** / "cắt lặng" | Bước 3 — bỏ khoảng lặng, từ đệm, câu vấp | "cắt mạnh" (lặng ≥0.4s) · "cắt nhẹ" (≥1.0s) · "giữ từ đệm" |
| **"khung dọc"** | Bước 1 — đưa về 9:16 | "crop giữa" · "nền mờ" |
| **"title hộp trắng"** / "hook" | Bước 5 bố cục `hook_box` | nội dung 2 dòng ("dòng 1: …, dòng 2: …") · "giữ đến giây X" |
| **"thumbnail kiểu <tên>"** | Bước 5, 1 trong 6 bố cục khác | `stack_hierarchy` · `magazine` · `serif_mix` · `lifestyle` · `brand_word` · `spaced_caps` |
| **"caption"** / "phụ đề chạy" | Bước 6 | "1 tiếng/lần" · "màu nhấn <màu>" · "caption cao hơn/thấp hơn" · "tắt caption" |
| **"chữ trượt"** / "slide" | Bước 7 — chữ/thẻ vào ra bằng trượt | "trượt nhanh" (0.25s) · "trượt chậm" (0.5s) |
| **"carousel 3D"** / "thẻ xoay quanh người" | Bước 8 | "ở giây A–B" · "dùng clip <tên>" · "xoay nhanh/chậm" · "viền sáng <màu>" · "thẻ to/nhỏ" · "vòng cao/thấp" · "không vòng sáng" |
| **"thẻ liệt kê"** | Bước 8b | "ở đoạn <câu>" · "tắt thẻ liệt kê" |

Ánh xạ tham số carousel 3D → `orbit_carousel.py`: xoay nhanh `--speed 60`,
chậm `--speed 25` · thẻ to `--card-w 360 --card-h 520`, nhỏ `--card-w 240
--card-h 350` · vòng cao/thấp: `--center-y` ±120 · viền sáng màu X `--glow X`
· không vòng sáng `--no-arc`.

Ví dụ lệnh khách:
- *"edit Dạng 1 plus, carousel 3D ở giây 0–4 và 12–15, xoay chậm"*
- *"chỉ cắt gọn + caption, tắt carousel"*
- *"title hộp trắng: dòng 1 'Toàn bộ video này', dòng 2 'được edit bằng AI'"*

## Tự đi lấy tài nguyên còn thiếu
Kiểm `assets/` trước → thiếu thì tự tải nguồn free-license → chỉ hỏi khách khi
không có nguồn hợp lệ hoặc cần đặc thù (logo, nhạc trend).

- **Font (TTF — cần cho cả libass lẫn HTML):** lấy thẳng từ repo Google Fonts:
  `curl.exe -L -o assets/fonts/BeVietnamPro-ExtraBold.ttf https://github.com/google/fonts/raw/main/ofl/bevietnampro/BeVietnamPro-ExtraBold.ttf`
  (tương tự `-Bold`, `-Regular`; Inter/Montserrat nằm ở `ofl/inter`,
  `ofl/montserrat`). Không dùng `.woff2` cho caption `.ass` — libass không đọc.
- **Icon** — Lucide (MIT): `curl.exe -L -o assets/icons/<ten>.svg https://unpkg.com/lucide-static/icons/<ten>.svg`.
- **SFX** (whoosh/pop) & **nhạc nền không lời** — WebSearch trên Pixabay /
  Mixkit, chỉ lấy khi trang ghi rõ "free for commercial use".
- **⚠️ Nhạc TREND** — KHÔNG tự tải (thường có bản quyền). Khách phải tự đưa
  file; không có thì hỏi lại hoặc gợi ý nhạc free-license thay thế.

## Khách phải tự cung cấp
- Video gốc (bắt buộc).
- 3–6 clip B-roll cho thẻ carousel 3D, để trong `input/broll/` (nên có; không
  có thì Agent lấy các đoạn khác trong video gốc, hoặc bỏ carousel 3D).
- Màu thương hiệu + logo (tuỳ chọn; không có → trắng chủ đạo, vàng nhấn).

## Khách chỉ cần làm gì
1. Đưa video vào `input/`.
2. Nói: *"edit Dạng 1 plus cho video này"*.

Agent tự: kiểm môi trường → tải font thiếu → chuẩn hoá 9:16 → transcribe →
cắt gọn → transcribe lại → viết title hook → carousel 3D (tách người + render
thẻ) → caption → slide + thẻ liệt kê (nếu có liệt kê) → ghép xuất → kiểm tra → báo đường dẫn `output/<tên-video>-dang1plus.mp4`.
