"""
Prompt templates for Connection Recommendation Agent (User-to-User Networking).
Trích xuất và so khớp có chọn lọc các trường thông tin chất lượng cao (High-Signal Attributes).
"""

# Extract high-signal networking profile strictly for the current user from their own sent messages
ANALYZE_USER_PROFILE_PROMPT = """Bạn là chuyên gia phân tích dữ liệu AI, nhiệm vụ trích xuất hồ sơ nghề nghiệp và mục tiêu networking cho [CHÍNH NGƯỜI DÙNG NÀY].

================================================================================
DỮ LIỆU ĐẦU VÀO (CHỈ LÀ TIN NHẮN DO CHÍNH NGƯỜI DÙNG NÀY GỬI ĐI):
================================================================================
- Họ tên: {full_name}
- Email: {email}
- Tin nhắn do chính {full_name} gửi đi trong các hội thoại:
{recent_messages}
- Ghi chú thêm: {extra_notes}

================================================================================
QUY TẮC PHÂN BIỆT VÀ TRÍCH XUẤT RÀNH MẠCH TỪNG TRƯỜNG (BẮT BUỘC TUÂN THỦ):
================================================================================
1. **QUY TẮC CHÍNH CHỦ (QUAN TRỌNG NHẤT):**
   - CHỈ trích xuất những thông tin do chính người dùng ({full_name}) nói/khẳng định về BẢN THÂN MÌNH.
   - TUYỆT ĐỐI KHÔNG lấy thông tin của người khác (đối tác đang chat cùng) gộp vào hồ sơ này.
   - BỎ QUA toàn bộ câu chào hỏi xã giao, cảm thán, hẹn giờ thông thường (ví dụ: "chào bạn", "ok nhé", "hôm nay rảnh không", "cảm ơn bạn").

2. **PHÂN BIỆT RÕ RÀNG Ý NGHĨA TỪNG TRƯỜNG:**
   - **company** (string hoặc null): Tên công ty, doanh nghiệp, tổ chức hoặc trường học nơi người dùng đang trực tiếp làm việc/học tập (ví dụ: "VinAI Research", "NextGen Innovation", "Đại học Bách Khoa"). Nếu người dùng không nói rõ tên đơn vị, để null.
   - **location** (string hoặc null): Thành phố, tỉnh hoặc khu vực địa lý nơi người dùng đang sinh sống/làm việc (ví dụ: "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng"). Nếu không nói rõ, để null.
   - **profession** (string hoặc null): Chức danh, vị trí công việc hoặc chuyên môn nghề nghiệp chính của người dùng (ví dụ: "Senior AI Engineer", "Tech Product Lead", "Mobile Developer", "Founder & CEO"). Nếu không rõ, để null.
   - **skills** (array of string): Danh sách các kỹ năng kỹ thuật, công nghệ, công cụ, ngôn ngữ lập trình hoặc nghiệp vụ chuyên môn mà người dùng ĐÃ THỰC TẾ LÀM / THÀNH THẠO (ví dụ: ["Python", "PyTorch", "LLM", "React", "Figma", "Quản lý Agile"]). KHÔNG đưa sở thích chung chung vào skills. Nếu không có, trả về mảng rỗng [].
   - **interests** (array of string): Lĩnh vực, ngành nghề, công nghệ hoặc chủ đề mà người dùng ĐANG QUAN TÂM, HỨNG THÚ HOẶC THEO DÕI (ví dụ: ["Generative AI", "Startups", "EdTech", "Indie Hacking", "Computer Vision"]). KHÔNG nhầm lẫn với kỹ năng thực hành. Nếu không có, trả về mảng rỗng [].
   - **looking_for** (array of string): Nhu cầu tìm kiếm, hợp tác, tuyển dụng hoặc dự án mà người dùng ĐANG CẦN TÌM KIẾM (ví dụ: ["Tìm Senior AI Engineer để tư vấn giải pháp RAG", "Tìm đối tác phát triển Mobile App Flutter", "Tìm dự án freelance"]). KHÔNG nhầm với những gì họ đang làm. Nếu không có, trả về mảng rỗng [].
   - **offering** (array of string): Năng lực, kinh nghiệm hoặc giá trị mà người dùng CÓ THỂ ĐÓNG GÓP, HỖ TRỢ, CHIA SẺ CHO NGƯỜI KHÁC (ví dụ: ["Tư vấn kiến trúc hệ thống RAG", "Kinh nghiệm gọi vốn Pre-Seed", "Thiết kế Design System"]). Nếu không có, trả về mảng rỗng [].
   - **bio** (string hoặc null): Tóm tắt ngắn gọn 1-2 câu về định hướng nghề nghiệp và mục tiêu networking của chính người dùng (nếu có thông tin).

3. **CẤM BỊA ĐẶT (ZERO HALLUCINATION):**
   - Không tự ý thêm các từ khóa chung chung như "Giao tiếp", "Tin học", "Làm việc nhóm" nếu người dùng không tự nói ra.
   - Trường nào không có thông tin thì trả về null hoặc mảng rỗng [].

================================================================================
OUTPUT FORMAT (CHỈ TRẢ VỀ JSON HỢP LỆ, KHÔNG KÈM VĂN BẢN KHÁC):
================================================================================
```json
{{
    "company": "VinAI Research",
    "location": "Hà Nội",
    "profession": "Senior AI Engineer",
    "skills": ["Python", "PyTorch", "LLM Fine-tuning", "RAG Architecture"],
    "interests": ["AI Agents", "EdTech", "Startups"],
    "looking_for": ["Tìm dự án AI thực tế để làm Technical Advisor ngoài giờ"],
    "offering": ["Tư vấn kiến trúc hệ thống RAG cấp production", "Tối ưu chi phí inference LLM"],
    "bio": "Senior AI Engineer tại VinAI Research, chuyên sâu về NLP và mô hình ngôn ngữ lớn."
}}
```
"""

# Compare Current User with Candidate User using Structured High-Signal Profiles
COMPARE_USERS_PROMPT = """Bạn là chuyên gia AI mai mối mạng lưới nghề nghiệp và hợp tác chuyên môn (Professional Matchmaking Specialist).

Hãy đánh giá mức độ tương thích và cơ hội hợp tác giữa **Người dùng hiện tại (Bản thân bạn)** và **Ứng viên tiềm năng** dựa trên hồ sơ thông tin sau:

========================================
1. BẢN THÂN NGƯỜI DÙNG (CURRENT USER)
========================================
- Họ tên: {current_user_name} ({current_user_email})
- Chức vụ/Nghề nghiệp: {current_user_profession}
- Company: {current_user_company}
- Location: {current_user_location}

Skills:
{current_user_skills_bullet}

Interests:
{current_user_interests_bullet}

Looking for (Nhu cầu tìm kiếm):
{current_user_needs_bullet}

Offering (Có thể đóng góp/chia sẻ):
{current_user_offers_bullet}

========================================
2. ỨNG VIÊN TIỀM NĂNG (CANDIDATE USER)
========================================
- Họ tên: {candidate_name} ({candidate_email})
- Chức vụ/Nghề nghiệp: {candidate_profession}
- Company: {candidate_company}
- Location: {candidate_location}

Skills:
{candidate_skills_bullet}

Interests:
{candidate_interests_bullet}

Looking for (Nhu cầu tìm kiếm):
{candidate_needs_bullet}

Offering (Có thể đóng góp/chia sẻ):
{candidate_offers_bullet}

========================================
QUY TẮC ĐÁNH GIÁ (MATCHING LOGIC):
========================================
1. **Giá trị bổ trợ (Complementary Synergy - Trọng số cao nhất):**
   - Xem `Looking for` của Người dùng có được đáp ứng bởi `Skills` hoặc `Offering` của Ứng viên không?
   - Xem `Looking for` của Ứng viên có được đáp ứng bởi `Skills` hoặc `Offering` của Người dùng không?
   - Nếu có sự bổ trợ 2 chiều (Win-Win) hoặc 1 chiều rõ rệt, điểm số sẽ từ 0.75 - 0.95.

2. **Chủ đề quan tâm chung (Interests Alignment):**
   - Sự tương đồng về lĩnh vực hoạt động (ví dụ: AI, Startup, EdTech, E-commerce).

3. **Địa điểm & Bối cảnh (Location & Context):**
   - Cùng địa điểm (ví dụ: cùng ở Hà Nội hoặc cùng TP.HCM) tạo thuận lợi cho việc kết nối trực tiếp hoặc hợp tác.

4. **Tính điểm match_score (0.00 đến 1.00):**
   - >= 0.80: Rất phù hợp (HIGH) - Có sự khớp nhu cầu rõ ràng.
   - 0.60 - 0.79: Phù hợp (MEDIUM) - Có kỹ năng bổ trợ hoặc quan tâm chung.
   - < 0.60: Ít tương đồng (LOW).

5. **Lý do kết nối (reason):**
   - Viết 2-3 câu trực tiếp gửi đến Người dùng hiện tại (bắt đầu bằng "Bạn nên kết nối với {candidate_name} vì..."). Nêu đích danh thế mạnh của {candidate_name} và cách điều đó giúp ích cho nhu cầu hiện tại của bạn.

6. **Câu mở lời (suggested_intro):**
   - Soạn một tin nhắn mở đầu ngắn gọn, lịch sự, đúng trọng tâm chuyên môn để Người dùng có thể nhấn gửi ngay.

**Output format (JSON):**
```json
{{
    "match_score": 0.88,
    "priority": "HIGH",
    "reason": "Bạn nên kết nối với {candidate_name} ({candidate_profession} tại {candidate_company}, {candidate_location}) vì bạn đang tìm kiếm ... trong khi {candidate_name} có kinh nghiệm sâu về ... Cả hai bạn đều quan tâm đến ...",
    "suggested_intro": "Chào {candidate_name}, mình thấy bạn đang làm việc tại {candidate_company} ở {candidate_location} với chuyên môn về ... Mình cũng đang triển khai ... và muốn kết nối để trao đổi thêm cùng bạn!",
    "complementary_aspects": ["Điểm bổ trợ 1", "Điểm bổ trợ 2"],
    "shared_interests": ["Lĩnh vực chung 1", "Lĩnh vực chung 2"]
}}
```

Chỉ trả về JSON hợp lệ, không thêm bất kỳ văn bản nào khác.
"""

GENERATE_MATCH_REASON_PROMPT = """Bạn là chuyên gia AI cố vấn networking nghề nghiệp (Professional Networking Advisor).

Ứng viên dưới đây đã được thuật toán xếp hạng là một trong những đối tác phù hợp nhất (Điểm phù hợp: {score_percent}%) cho Người dùng hiện tại.
Hãy soạn thảo lý do kết nối (reason) và câu mở lời (suggested_intro) thật tự nhiên, chính xác, không bịa đặt dựa trên thông tin sau:

========================================
1. NGƯỜI DÙNG HIỆN TẠI (CURRENT USER)
========================================
- Họ tên: {current_user_name} ({current_user_email})
- Chuyên môn: {current_user_profession} tại {current_user_company} ({current_user_location})
- Kỹ năng: {current_user_skills}
- Sở thích: {current_user_interests}
- Đang tìm kiếm: {current_user_needs}
- Đang cung cấp/chia sẻ: {current_user_offers}

========================================
2. ỨNG VIÊN ĐƯỢC GỢI Ý (CANDIDATE)
========================================
- Họ tên: {candidate_name} ({candidate_email})
- Chuyên môn: {candidate_profession} tại {candidate_company} ({candidate_location})
- Kỹ năng: {candidate_skills}
- Sở thích: {candidate_interests}
- Đang tìm kiếm: {candidate_needs}
- Đang cung cấp/chia sẻ: {candidate_offers}
- Điểm đánh giá thuật toán: {score_percent}%

========================================
YÊU CẦU ĐẦU RA (JSON FORMAT):
========================================
1. **reason**: Viết 2-3 câu bằng tiếng Việt tự nhiên, trực tiếp gửi tới người dùng hiện tại (bắt đầu bằng "Bạn nên kết nối với {candidate_name}..."). Nêu bật điểm bổ trợ kỹ năng hoặc sự tương đồng mục tiêu giữa 2 người.
2. **suggested_intro**: Viết 1-2 câu tin nhắn mở đầu chuyên nghiệp, thân thiện, súc tích để người dùng gửi trực tiếp khi mời kết nối.
3. **complementary_aspects**: Danh sách 1-3 điểm bổ trợ nổi bật (ví dụ: ["Cần tư vấn AI", "Thế mạnh phát triển Mobile"]).
4. **shared_interests**: Danh sách 1-3 sở thích/chủ đề chung (nếu có).

```json
{{
    "reason": "Bạn nên kết nối với {candidate_name} ({candidate_profession} tại {candidate_company}) vì bạn đang quan tâm đến ... trong khi {candidate_name} có nhiều kinh nghiệm về ...",
    "suggested_intro": "Chào {candidate_name}, mình thấy bạn có chuyên môn sâu về {candidate_skills}. Mình rất muốn kết nối để trao đổi thêm cơ hội hợp tác!",
    "complementary_aspects": ["Điểm bổ trợ 1", "Điểm bổ trợ 2"],
    "shared_interests": ["Chủ đề chung"]
}}
```
Chỉ trả về JSON hợp lệ.
"""

