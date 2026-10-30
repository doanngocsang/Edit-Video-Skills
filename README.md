# Claude Video Skills — edit video talking-head dọc 9:16

Bộ 2 skill cho Claude giúp edit video **talking-head** (1 người nói trước
camera) thành video ngắn dọc 9:16 cho TikTok / Reels / Shorts. Bạn chỉ cần đưa
video vào và nói 1 câu, Claude tự cài công cụ, tự cắt gọn, tự viết tiêu đề,
tự dựng hiệu ứng và xuất file.

| Skill | Phong cách | Câu gọi |
|---|---|---|
| [`dang-1-plus-slide-carousel`](skills/dang-1-plus-slide-carousel/SKILL.md) | Cắt gọn + title hook hộp trắng + caption động + **carousel 3D** (các thẻ video xoay vòng quanh người nói) + thẻ liệt kê + chữ trượt | *"edit Dạng 1 plus cho video này"* |
| [`explainer-chia-doi`](skills/explainer-chia-doi/SKILL.md) | **Video hướng dẫn chia đôi màn hình**: nửa trên đồ hoạ (tiêu đề hộp đỏ, icon bật lên, ảnh chụp cuộn, gõ chữ, nhãn số liệu, lưới video, thẻ so sánh, sơ đồ nhánh), nửa dưới khung mặt bo góc, caption từng từ | *"edit explainer chia đôi cho video này"* |

📘 **Hướng dẫn chi tiết từng phong cách, hiệu ứng và tên gọi:** [HUONG-DAN-SU-DUNG.md](HUONG-DAN-SU-DUNG.md)

## ⚡ Cài nhanh

### Cách A — Dán câu này vào Claude Code (Claude tự cài)
```text
Cài bộ skill từ https://github.com/doanngocsang/Edit-Video-Skills: tải repo về, chép mọi thư mục bên trong thư mục skills/ vào thư mục skill cá nhân của Claude Code (Windows: %USERPROFILE%\.claude\skills\ — macOS/Linux: ~/.claude/skills/), ghi đè nếu đã có. Sau đó kiểm tra mỗi thư mục có SKILL.md và thư mục scripts/, rồi báo lại danh sách skill đã cài.
```
Cài xong, **thoát và mở lại Claude Code** để skill được nạp.

### Cách B — 1 dòng lệnh trong terminal
**Windows (PowerShell):**
```powershell
$t="$env:TEMP\cvs"; Remove-Item $t,"$t.zip" -Recurse -Force -EA 0; Invoke-WebRequest https://github.com/doanngocsang/Edit-Video-Skills/archive/refs/heads/main.zip -OutFile "$t.zip"; Expand-Archive "$t.zip" $t -Force; New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null; Copy-Item "$t\Edit-Video-Skills-main\skills\*" "$env:USERPROFILE\.claude\skills\" -Recurse -Force; Write-Host "Da cai xong"
```
**macOS / Linux:**
```bash
git clone --depth 1 https://github.com/doanngocsang/Edit-Video-Skills /tmp/cvs && mkdir -p ~/.claude/skills && cp -R /tmp/cvs/skills/* ~/.claude/skills/ && rm -rf /tmp/cvs && echo "Da cai xong"
```
Sau đó mở Claude Code trong thư mục dự án video và gọi: *"edit Dạng 1 plus cho
video này"* hoặc *"edit explainer chia đôi cho video này"*. Lần chạy đầu
Claude tự cài ffmpeg / thư viện Python còn thiếu.

## Cài đặt thủ công

### Cách 1 — Claude Code (khuyên dùng, chạy trên máy bạn)
1. Tải repo này về (nút **Code → Download ZIP** trên GitHub, hoặc `git clone`).
2. Chép từng thư mục trong `skills/` vào thư mục skill cá nhân của Claude Code:
   - Windows: `C:\Users\<tên-bạn>\.claude\skills\`
   - macOS / Linux: `~/.claude/skills/`

   Kết quả đúng: `.claude/skills/explainer-chia-doi/SKILL.md` (và
   `scripts/` nằm cạnh SKILL.md).
3. Mở Claude Code trong thư mục dự án video của bạn và gọi skill bằng câu ở
   bảng trên.

### Cách 2 — Tải lên Claude (claude.ai)
Mỗi skill có sẵn file zip riêng trong mục **Releases** (hoặc tự nén từng thư
mục trong `skills/`). Vào phần Skills trong Settings của Claude và tải file
zip lên. Lưu ý: skill cần ffmpeg, Python và tải model từ internet — chạy tốt
nhất khi Claude làm việc trực tiếp trên máy bạn (Claude Code hoặc ứng dụng
desktop được liên kết với máy).

## Yêu cầu
Lần chạy đầu Claude sẽ tự kiểm tra và cài phần còn thiếu:
- **ffmpeg** (có libass) — Windows: `winget install Gyan.FFmpeg` · macOS: `brew install ffmpeg`
- **Python 3.10+** với `faster-whisper`, `playwright` (+ Chromium), `pillow`;
  skill carousel 3D cần thêm `mediapipe`, `opencv-python`.
- **Internet** ở lần đầu để tải model nhận dạng giọng nói (Whisper) và model
  tách người (MediaPipe), font Google Fonts, icon.

Đã cài ffmpeg / Python cho skill khác rồi thì không cần cài lại.

## Cấu trúc thư mục dự án khi dùng
```
du-an-video/
├─ input/          ← video nói chuyện
│  ├─ broll/       ← (Dạng 1 plus) 3–6 clip cho thẻ carousel 3D
│  └─ shots/       ← (Explainer) ảnh chụp màn hình để minh hoạ
├─ assets/{fonts,icons}/   ← tự tải nếu thiếu
├─ work/           ← file trung gian
└─ output/         ← thành phẩm
```

## Gọi riêng từng hiệu ứng
Xem đầy đủ trong [HUONG-DAN-SU-DUNG.md](HUONG-DAN-SU-DUNG.md). Mỗi skill cũng có bảng **"Gọi từng hiệu ứng"** trong SKILL.md. Ví dụ:
- *"edit Dạng 1 plus, carousel 3D ở giây 0–4, xoay chậm, viền sáng xanh"*
- *"chỉ cắt gọn + caption, tắt carousel"*
- *"edit explainer chia đôi, nền tối, giây 8 dùng ảnh chat.png cuộn hết kèm nhãn 47.8K followers"*

## Lưu ý
- **Nhạc trend / nhạc có bản quyền**: skill không tự tải; bạn tự cung cấp file
  có quyền sử dụng.
- **Logo thương hiệu** lấy từ Simple Icons (CC0); logo không có sẵn (vd
  ChatGPT) bạn tự đặt vào `assets/icons/`.
- Phiên bản đầu (0.1): pipeline dựng đồ hoạ và ghép đã chạy thử với video giả
  lập; phần tách người (MediaPipe) nên kiểm tra mép tóc/vai ở lần đầu trên
  video thật. Góp ý và lỗi: mở Issue trên GitHub.

## Giấy phép
MIT — xem [LICENSE](LICENSE).
