# Hướng dẫn sử dụng — phong cách, hiệu ứng & tên gọi

Tài liệu này giải thích từng **phong cách** và từng **hiệu ứng** trong bộ skill,
kèm **tên gọi** để bạn ra lệnh cho Claude, **khi nào nên dùng** và **câu lệnh
mẫu**. Bạn không cần biết kỹ thuật — chỉ cần gọi đúng tên.

---

## 0. Thuật ngữ cơ bản

| Thuật ngữ | Nghĩa dễ hiểu |
|---|---|
| **Talking head** | Kiểu *cảnh quay*: 1 người nhìn camera và nói (khung đầu–vai/ngực). Cả 2 skill đều dùng cho loại cảnh quay này. |
| **Phong cách edit** | Cách *dựng* đặt lên cảnh quay: tối giản, hiệu ứng thị giác, explainer có đồ hoạ… |
| **Hook** | 1–3 giây đầu giữ chân người xem (tiêu đề gây tò mò, hiệu ứng mạnh). |
| **Jump cut** | Cắt bỏ đoạn thừa và nối thẳng, hình "nhảy" nhẹ — tạo nhịp nhanh. |
| **B-roll** | Cảnh quay phụ chèn vào (cảnh khác, sản phẩm, màn hình…), không phải cảnh nói chính. |
| **Caption** | Phụ đề chạy theo lời nói. |
| **Accent / màu nhấn** | Màu nổi bật dùng cho từ khoá (vàng, đỏ…). |
| **9:16** | Khung dọc 1080×1920 của TikTok / Reels / Shorts. |

---

## 1. Phong cách **"Dạng 1 Plus"** (skill `dang-1-plus-slide-carousel`)

**Trông như thế nào:** video nói chuyện được cắt gọn sạch sẽ, mở đầu bằng tiêu
đề có 1 dòng nằm trong hộp trắng, caption chạy theo lời, và điểm nhấn là
**các thẻ video xoay vòng quanh người nói** như vệ tinh.

**Hợp với:** giới thiệu bản thân/dịch vụ, khoe nhiều mẫu sản phẩm/nhiều dự án,
video "toàn bộ video này được làm bằng…", portfolio, video bán hàng ngắn.

**Câu gọi:** *"edit Dạng 1 plus cho video này"*

**Chuẩn bị:** video nói chuyện trong `input/`; **3–6 clip ngắn** (cảnh khác,
trang phục khác, sản phẩm…) trong `input/broll/` cho các thẻ xoay.

### Các hiệu ứng

#### 1.1 Cắt gọn — gọi: **"cắt gọn"** / "cắt lặng"
- **Làm gì:** bỏ khoảng lặng dài, từ đệm ("ừm", "à", "kiểu như"), câu nói vấp
  (giữ lần nói tốt nhất), đoạn thừa đầu/cuối ("ok quay nhé").
- **Tuỳ chỉnh:** "cắt mạnh" (bỏ cả khoảng nghỉ ngắn → nhịp rất nhanh) · "cắt
  nhẹ" (chỉ bỏ khoảng lặng rất dài → tự nhiên) · "giữ từ đệm".
- **An toàn:** nếu phải cắt hơn 40% video, Claude dừng lại hỏi bạn trước.

#### 1.2 Khung dọc — gọi: **"khung dọc"**
- **Làm gì:** đưa video về 9:16. Video ngang → **"crop giữa"** (cắt lấy phần
  giữa) hoặc **"nền mờ"** (video nằm giữa, nền là chính video làm mờ).

#### 1.3 Title hộp trắng — gọi: **"title hộp trắng"** / "hook"
- **Trông như:** 2 dòng ở phía trên; dòng 1 chữ trắng đậm, **dòng 2 chữ đen
  trong hộp trắng bo góc**. Video vẫn chạy phía sau.
- **Khi nào:** mặc định cho hook mở đầu khi có carousel 3D.
- **Ví dụ:** *"title hộp trắng: dòng 1 'Toàn bộ video này', dòng 2 'được edit
  bằng AI'"* · "giữ title đến giây 5".

#### 1.4 Thumbnail mở đầu kiểu khác — gọi: **"thumbnail kiểu <tên>"**
Nếu không dùng title hộp trắng, chọn 1 trong 6 kiểu (hiện ~2.5s đầu rồi
trượt lên):

| Tên | Trông như | Hợp với |
|---|---|---|
| `stack_hierarchy` | Chữ xếp tầng to nhỏ | Bán hàng, tuyên bố mạnh |
| `magazine` | Tiêu đề gọn + số tập | Series, "Tập 3" |
| `serif_mix` | Chữ có chân nghiêng sang trọng | Câu hỏi, chia sẻ suy ngẫm |
| `lifestyle` | Chữ thường thân thiện | Vlog đời thường |
| `brand_word` | 1 từ thương hiệu thật to + phụ đề nhỏ | Xây thương hiệu |
| `spaced_caps` | CHỮ IN HOA GIÃN CÁCH | Studio, agency |

#### 1.5 Caption — gọi: **"caption"** / "phụ đề chạy"
- **Trông như:** chữ trắng đậm, 2–4 tiếng mỗi lần, tiếng đang nói tô màu nhấn,
  nằm dưới mặt.
- **Tuỳ chỉnh:** "1 tiếng/lần" · "màu nhấn đỏ" · "caption cao hơn/thấp hơn" ·
  "tắt caption".

#### 1.6 Chữ trượt — gọi: **"chữ trượt"** / "slide"
- **Trông như:** mọi chữ/thẻ xuất hiện và biến mất bằng chuyển động trượt mượt
  (không mờ dần, không xoay).
- **Tuỳ chỉnh:** "trượt nhanh" · "trượt chậm".

#### 1.7 ⭐ Carousel 3D — gọi: **"carousel 3D"** / "thẻ xoay quanh người"
- **Trông như:** 3–6 thẻ video bo góc viền trắng **xoay vòng quanh người nói
  ở tầm ngực**. Thẻ đi phía sau bị người che, thẻ đi phía trước đè lên người,
  thẻ gần camera nhất **phát sáng viền cam**, có **vòng sáng quỹ đạo** bên dưới.
- **Khi nào:** đoạn hook mở đầu; khi nói "nhiều video / nhiều kiểu / mình có
  thể làm…". Tối đa 3 lần/video, mỗi lần 3–5 giây.
- **Tuỳ chỉnh:**

  | Nói | Kết quả |
  |---|---|
  | "ở giây 0–4" | Chọn đoạn xuất hiện |
  | "dùng clip a, b, c" | Chọn clip trong thẻ |
  | "xoay nhanh" / "xoay chậm" | Tốc độ quay |
  | "thẻ to" / "thẻ nhỏ" | Kích thước thẻ |
  | "vòng cao hơn" / "vòng thấp hơn" | Đưa vòng lên/xuống (theo vị trí ngực) |
  | "viền sáng xanh" (màu bất kỳ) | Màu phát sáng |
  | "không vòng sáng" | Bỏ vòng quỹ đạo |
  | "thẻ đừng che mặt" | Thẻ phía trước mờ dần khi đi ngang mặt |

#### 1.8 Thẻ liệt kê — gọi: **"thẻ liệt kê"**
- **Trông như:** khi bạn nói "3 bước", "thứ nhất… thứ hai…", mỗi ý hiện thành 1
  thẻ trắng có số thứ tự ở phía trên, thẻ mới trượt vào – thẻ cũ trượt ra, có
  chấm chỉ báo ●○○.
- **Tuỳ chỉnh:** "ở đoạn <câu>" · "tắt thẻ liệt kê".

### Câu lệnh mẫu
- *"edit Dạng 1 plus cho video này"* — tự động hết.
- *"edit Dạng 1 plus, carousel 3D ở giây 0–4 và 12–15, xoay chậm, viền sáng trắng"*
- *"chỉ cắt gọn + caption, tắt carousel"*
- *"edit Dạng 1 plus, cắt mạnh, caption 1 tiếng/lần màu vàng"*

---

## 2. Phong cách **"Explainer chia đôi"** (skill `explainer-chia-doi`)

**Trông như thế nào:** kiểu video **hướng dẫn / chia sẻ kiến thức**. Màn hình
chia đôi: **nửa trên là đồ hoạ minh hoạ** đúng điều bạn đang nói, **nửa dưới là
khung mặt bo góc**. Xen kẽ vài đoạn mặt toàn màn hình. Mỗi ý có tiêu đề với từ
khoá trong hộp đỏ.

**Hợp với:** hướng dẫn dùng công cụ (ChatGPT, Canva…), mẹo theo bước, phân
tích số liệu, so sánh, review phần mềm, chia sẻ kinh nghiệm có minh hoạ.

**Câu gọi:** *"edit explainer chia đôi cho video này"*

**Chuẩn bị:** video nói chuyện trong `input/`; **ảnh chụp màn hình** (trang
kênh, câu trả lời AI, bảng số…) trong `input/shots/`; logo không có sẵn (vd
ChatGPT) để trong `assets/icons/`. Không có ảnh vẫn làm được bằng icon, gõ
chữ, số liệu, sơ đồ.

### Các hiệu ứng

#### 2.1 Chia đôi / toàn màn hình — gọi: **"chia đôi"**, **"toàn màn hình"**
- **Chia đôi:** đồ hoạ trên, mặt dưới — dùng khi nói về bước, công cụ, con số,
  ví dụ (60–80% video).
- **Toàn màn hình:** chỉ mặt người — dùng lúc chào, hook cảm xúc, chuyển ý, kết.
- **Ví dụ:** "giây 5–9 chia đôi", "đoạn kết toàn màn hình".

#### 2.2 Tiêu đề hộp đỏ — gọi: **"tiêu đề hộp đỏ"**
- **Trông như:** chữ đậm + **từ khoá trong hộp đỏ** + dòng phụ chữ *nghiêng có
  chân*. VD: "Cách dùng **ChatGPT**" / *tối ưu kênh TikTok*; "Bước 2: **Gửi link
  kênh**".
- **Tuỳ chỉnh:** "tiêu đề: Bước 1 / Truy cập ChatGPT" · "dòng phụ: …" · "màu
  hộp xanh" (đổi màu nhấn cả video).

#### 2.3 Icon bật lên — gọi: **"icon bật lên"**
- **Trông như:** logo trong ô vuông trắng bo góc **nảy ra** đúng lúc bạn nhắc
  tên (ChatGPT, TikTok, Facebook, YouTube…), có thể kèm chữ bên dưới.
- **Ví dụ:** "logo TikTok ở giây 4".

#### 2.4 Ảnh chụp cuộn — gọi: **"ảnh chụp cuộn"**
- **Trông như:** ảnh chụp màn hình trong **khung viền đỏ bo góc có bóng**, tự
  **cuộn chậm xuống** để lộ thêm nội dung (ảnh dài); có thể gắn 2 logo tròn ở 2
  góc trên.
- **Tuỳ chỉnh:** "dùng ảnh chat.png" · "cuộn hết" · "không cuộn" · "gắn logo
  TikTok, Facebook 2 góc".

#### 2.5 Gõ chữ — gọi: **"gõ chữ"**
- **Trông như:** ô chat tối giống ô nhập của ChatGPT, **chữ hiện dần từng ký
  tự** kèm con trỏ nhấp nháy — minh hoạ bạn đang gõ câu lệnh.
- **Tuỳ chỉnh:** "gõ: phân tích kênh tiktok này…" · "gõ nhanh" · "gõ chậm".

#### 2.6 Nhãn số liệu — gọi: **"nhãn số liệu"**
- **Trông như:** thẻ đỏ chữ trắng ("**47.8K** FOLLOWERS", "**61.000** BÀI CAO
  NHẤT") **bay vào từ 2 bên**, lần lượt từng cái, thường nằm cạnh ảnh chụp.
- **Ví dụ:** "47.8K followers bên trái, 1.9M view bên phải".

#### 2.7 Lưới video — gọi: **"lưới video"**
- **Trông như:** lưới ảnh bìa video (6 cột), vài ô nổi bật được **viền đỏ +
  gắn số view** (▶ 100.4K…).
- **Ví dụ:** "đánh dấu 3 video đầu: 100.4K, 107.5K, 98.6K".

#### 2.8 Thẻ so sánh — gọi: **"thẻ so sánh"**
- **Trông như:** 2 thẻ tối cạnh nhau trượt vào lần lượt: avatar + tên + nhãn
  ("CỦA BẠN" xám / "ĐỐI THỦ" đỏ) + "✓ Đã phân tích".
- **Ví dụ:** "Kênh của bạn vs Đối thủ", "Trước vs Sau".

#### 2.9 Sơ đồ nhánh — gọi: **"sơ đồ nhánh"**
- **Trông như:** 3 logo nguồn ở trên, **đường cong đỏ tự vẽ** hội tụ vào 1
  logo ở giữa, rồi hiện **ô kết quả**.
- **Ví dụ:** "TikTok, Facebook, YouTube → ChatGPT → Báo cáo phân tích kênh".

#### 2.10 Chữ to — gọi: **"chữ to"**
- **Trông như:** 1 từ/cụm rất to bật lên giữa vùng đồ hoạ — cho câu chốt.
- **Ví dụ:** *"chữ to 'MIỄN PHÍ' ở giây 20"*.

#### 2.11 Caption từng từ — gọi: **"caption"**
- **Trông như:** mỗi lần 1 từ, nằm giữa đồ hoạ và khung mặt; **tự đổi màu**
  (chữ đen trên nền sáng, chữ trắng trên nền tối).
- **Tuỳ chỉnh:** "tắt caption đoạn …".

#### 2.12 Nền sáng / nền tối — gọi: **"nền sáng"**, **"nền tối"**
- Nền kem chữ đen (nhẹ nhàng, mở đầu) hoặc nền đen chữ trắng (nội dung chính).
- **Ví dụ:** "cả video nền tối".

### Câu lệnh mẫu
- *"edit explainer chia đôi cho video này"* — tự động hết.
- *"edit explainer chia đôi, nền tối, 3 giây đầu toàn màn hình"*
- *"giây 8 dùng ảnh chat.png cuộn hết kèm nhãn 47.8K followers bên trái"*
- *"đoạn nói về 3 nền tảng làm sơ đồ nhánh, kết quả là 'Báo cáo phân tích kênh'"*
- *"đổi màu nhấn sang xanh dương #1E6BFF"*

---

## 3. Chọn phong cách nào?

| Video của bạn… | Dùng |
|---|---|
| Nói chuyện tự nhiên, muốn ấn tượng thị giác, có nhiều clip phụ | **Dạng 1 Plus** |
| Hướng dẫn từng bước, có ảnh chụp màn hình/số liệu | **Explainer chia đôi** |
| Chỉ cần sạch, nhanh, không hiệu ứng | Dạng 1 Plus + *"chỉ cắt gọn + caption, tắt carousel"* |

## 4. Mẹo để ra video đẹp
- Quay **dọc**, mặt ở khoảng 1/3 trên khung, ánh sáng đủ, nền gọn — tách người
  (carousel 3D) sẽ sạch hơn.
- Nói **rõ từ khoá** ("bước 1", "ChatGPT", "47 nghìn") — đồ hoạ bám theo đúng
  lúc bạn nói từ đó.
- Ảnh chụp màn hình nên **rõ, không mờ**; ảnh dài (chụp cuộn) hợp với "ảnh chụp cuộn".
- Muốn sửa nhỏ sau khi xem bản đầu: nói thẳng với Claude bằng tên hiệu ứng, VD
  *"carousel xoay chậm lại"*, *"giây 12 bỏ lưới video"* — Claude chỉ sửa phần đó.
