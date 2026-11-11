# Ghi chú phân tích · Day 04

Họ và tên: Phạm Ngọc Trung Quân
MSSV: 2A202603626

## 1. Case được chọn

- ID case: H8
- Câu trả lời của agent:"Câu trả lời thiếu sót thông tin quan trọng về giới hạn số lượng sự cố và không làm rõ rằng đây chỉ là danh sách các sự cố gần nhất, không bảo đảm tính đầy đủ cho giai đoạn 2020–2026."
- Điểm ở lần chạy 1: 60

## 2. Bằng chứng trong trace

Dán đoạn trace chứng minh lỗi và nêu nguyên nhân có thể xảy ra.

```text
Tool get_status trả về kết quả có trường cảnh báo và số lượng giới hạn:
"matching_incidents_in_last_50": 50,
"note": "Chỉ tìm theo chuỗi trong 50 incident gần nhất; không tìm thấy không chứng minh không có sự cố.",
"source": "https://www.githubstatus.com"

Tuy nhiên, trong câu trả lời, agent chỉ nói chung chung: "giới hạn trong việc lấy dữ liệu và chỉ tìm kiếm trong các sự cố gần nhất" mà KHÔNG nêu rõ con số giới hạn kỹ thuật cụ thể (chỉ lưu tối đa 50 incident gần nhất).

Judge chấm điểm: 60/100
- Reason: "Câu trả lời thiếu sót thông tin quan trọng về giới hạn số lượng sự cố và không làm rõ rằng đây chỉ là danh sách các sự cố gần nhất, không bảo đảm tính đầy đủ cho giai đoạn 2020–2026."
- Improvement: "Cần thừa nhận rõ ràng rằng danh sách chỉ bao gồm các sự cố trong phạm vi giới hạn và không đảm bảo tính đầy đủ của thông tin cho toàn bộ giai đoạn yêu cầu."
```

## 3. Thay đổi đã thực hiện

- Sửa gì, ở đâu: 
  - Cải tiến SYSTEM_PROMPT trong agent.py: Bổ sung nguyên tắc xử lý ranh giới dữ liệu: khi người dùng yêu cầu toàn bộ dữ liệu lịch sử hoặc danh sách không sót, agent phải nêu rõ ngay giới hạn dữ liệu (chỉ quét tối đa 50 incident gần nhất) và khẳng định không thể bao quát toàn bộ giai đoạn 2020–2026.
  - Bổ sung cơ chế Evidence Gate trong agent.py: Tự động kiểm tra xem final answer đã dẫn URL nguồn của incident đã đọc hay chưa; nếu thiếu và còn lượt gọi thì yêu cầu model bổ sung (đáp ứng tiêu chí Bài 4 và pass 2 test validation còn lại).
- Vì sao chọn thay đổi này:
  - Giúp cải thiện trực tiếp tiêu chí boundaries (15đ) và completeness (25đ) của case H8, tránh việc model tạo ấn tượng sai lệch rằng danh sách đưa ra là đầy đủ.
  - Đảm bảo toàn bộ 37/37 unit tests của lab đều PASS.

## 4. So sánh hai lần chạy

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 82.27 / 100 | 85.45 / 100 |
| Điểm case đã chọn | 60/100 | 100/100 |
| Số model calls | 52 calls / 2 calls | 48 calls / 1 call |
| Token, chi phí nếu có | $0.01078 / $0.00073 | $0.01435 / $0.00025 |

- Lỗi đã giải quyết:
  - Case H8 (Ranh giới dữ liệu): Tăng vọt từ 60 lên 100/100. Agent đã chủ động nêu rõ giới hạn kỹ thuật 50 sự cố ngay từ đầu và từ chối cam kết tính đầy đủ cho toàn bộ giai đoạn dài 2020–2026 thay vì tìm kiếm mù quáng hoặc phát biểu chung chung.
  - Mở khóa trần điểm cơ học cho H1 và H6: Ở lần 1, H1 và H6 chỉ đạt 60 điểm do bị chặn trần (vi phạm min_tool_steps: 2 vì dừng lại sau 1 bước gọi tool). Ở lần 2, nhờ chỉ dẫn điều tra theo chuỗi liên kết, agent đã gọi tiếp get_incident_details cho sự cố gộp xr3myzj7ms51 ở bước 2, giúp H1 đạt 100/100 và H6 đạt 80/100.
  - Phân định rõ ranh giới & bằng chứng (A1, A8, H3): A1 tăng từ 80 lên 100, A8 tăng từ 85 lên 100, H3 tăng từ 85 lên 100 nhờ phân biệt chính xác sự cố lịch sử đã resolved và sự cố đang theo dõi (monitoring), đồng thời dẫn đủ URL nguồn thông qua Evidence Gate.
- Lỗi còn lại hoặc mới xuất hiện:
  - Xuất hiện sự dao động điểm nhẹ (variance) ở một vài case do tính chất sinh văn bản ngẫu nhiên của model và tiêu chí chấm bằng LLM Judge (ví dụ E2 từ 95 xuống 70, A5 từ 65 xuống 55, H4 từ 100 xuống 80).
  -  Chi phí và lượng token ở lần chạy 2 tăng nhẹ (tổng chi phí tăng từ $0.0107 lên $0.0143) do System Prompt chi tiết hơn và agent thực hiện gọi thêm tool ở bước 2 đối với các case có chuỗi liên kết.

## 5. Giới hạn

- Giới hạn của điểm Judge (LLM-as-a-Judge): Việc dùng một mô hình ngôn ngữ (GPT-4o-mini) làm giám khảo đánh giá mang tính chất phỏng đoán (heuristic evaluation). Judge có thể quá nhạy cảm với cách dùng từ hoặc ngữ cảnh cụ thể, dẫn đến việc cùng một câu trả lời đúng bản chất nhưng điểm số có thể dao động từ cộng trừ 5 đến cộng trừ 15 điểm giữa các lần đánh giá do tính ngẫu nhiên (temperature) của quá trình sinh văn bản.
- Giới hạn của Snapshot (Mock Data): Dữ liệu kiểm thử chỉ là một tập snapshot tĩnh được đóng băng tại một thời điểm cố định (tháng 11/2026) với giới hạn tối đa 50 incidents gần nhất. Môi trường này chưa thể hiện được tính thời gian thực (real-time dynamic streams) của hệ thống thực tế, nơi dữ liệu trạng thái thay đổi liên tục theo từng giây.
- Giới hạn của việc chỉ chạy một lần mỗi phiên bản (Single-run evaluation): Việc chỉ chạy một lần duy nhất cho mỗi phiên bản (N=1) mang tính cục bộ (single sample point), dễ bị ảnh hưởng bởi độ trễ API, biến thiên stochastic của model hoặc lỗi ngẫu nhiên từ mạng. Để khẳng định chắc chắn về mặt thống kê rằng phiên bản mới vượt trội ổn định, cần chạy lặp lại nhiều lần (N
≥
≥ 3 hoặc 5) và tính toán điểm trung bình cùng độ lệch chuẩn.
