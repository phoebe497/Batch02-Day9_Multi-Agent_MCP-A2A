# BÁO CÁO KẾT QUẢ THỰC HÀNH CODELAB
## HỆ THỐNG MULTI-AGENT VỚI A2A PROTOCOL

### THÔNG TIN CÁ NHÂN
- **Họ và tên:** Nguyễn Như Yến Phương
- **Mã học viên:** 2A202600616
- **Lớp:** E403

---

## PHẦN A: TRẢ LỜI CÂU HỎI LÝ THUYẾT & PHÂN TÍCH CODE

### PHẦN 1: Direct LLM Calling (Gọi LLM trực tiếp)

**1. LLM được khởi tạo như thế nào? (Hàm `get_llm()`)**
- LLM được khởi tạo bằng cách gọi hàm `get_llm()` trong [common/llm.py](common/llm.py).
- Hàm này trả về một đối tượng `ChatOpenAI` từ thư viện `langchain_openai`, kết nối tới endpoint tương thích với OpenAI của mô hình đích (ví dụ: Mistral API `https://api.mistral.ai/v1` hoặc Groq API `https://api.groq.com/openai/v1`) thông qua các biến cấu hình từ môi trường (`MISTRAL_API_KEY`, `GROQ_API_KEY`, `LLM_MODEL`).

**2. Message được gửi đến LLM có cấu trúc gì?**
- Danh sách tin nhắn gửi đi là một mảng tuần tự chứa các đối tượng Message của LangChain:
  - `SystemMessage`: Thiết lập cấu hình hệ thống, hướng dẫn nhiệm vụ, vai trò và định dạng phản hồi cho AI.
  - `HumanMessage`: Nội dung câu hỏi cụ thể của người dùng (`QUESTION`).

**3. Tại sao cần có `SystemMessage` và `HumanMessage`?**
- `SystemMessage`: Dùng để định hình vai trò chuyên gia (ví dụ: *"Bạn là một chuyên gia pháp lý..."*), định dạng phản hồi và kiểm soát ranh giới hoạt động của AI.
- `HumanMessage`: Đại diện cho câu hỏi trực tiếp hoặc dữ liệu người dùng đưa vào trong phiên chat hiện tại.
- **Ý nghĩa:** Sự phân tách rõ ràng này giúp mô hình AI phân biệt được đâu là quy tắc vận hành hệ thống (System) và đâu là dữ liệu đầu vào cần xử lý (Human), giúp chống lại các cuộc tấn công Prompt Injection và đảm bảo phản hồi đi đúng trọng tâm.

---

### PHẦN 2: LLM + RAG & Tools (Kết hợp RAG và Công cụ)

**1. Hàm `@tool` decorator được dùng ở đâu?**
- Decorator `@tool` (được import từ `langchain_core.tools`) được đặt ngay phía trên định nghĩa của hai hàm trong [stages/stage_2_rag_tools/main.py](stages/stage_2_rag_tools/main.py):
  - Hàm `search_legal_database`: Tìm kiếm thông tin luật trong cơ sở dữ liệu tri thức pháp lý.
  - Hàm `calculate_damages`: Ước tính số tiền bồi thường thiệt hại vi phạm hợp đồng.

**2. `LEGAL_KNOWLEDGE` được cấu trúc như thế nào?**
- `LEGAL_KNOWLEDGE` là một danh sách (list) chứa các đối tượng dictionary đại diện cho cơ sở dữ liệu tri thức giả lập. Mỗi đối tượng gồm:
  - `id`: Định danh duy nhất cho điều luật (ví dụ: `ucc_breach`, `labor_law`).
  - `keywords`: Danh sách các từ khóa dùng để đối sánh từ khóa (keyword match) với câu hỏi của người dùng.
  - `text`: Nội dung văn bản luật chi tiết để cung cấp ngữ cảnh trả lời cho LLM.

**3. LLM được bind với tools ra sao? (Tìm `.bind_tools()`)**
- LLM được liên kết với danh sách các công cụ bằng phương thức `.bind_tools()`:
  ```python
  llm_with_tools = llm.bind_tools(TOOLS)
  ```
  Phương thức này chuyển hóa cấu trúc tham số (signature) và tài liệu docstring của các hàm `@tool` thành định dạng JSON schema truyền cho mô hình AI, giúp mô hình biết lúc nào nên gọi công cụ nào và truyền tham số gì.

---

### PHẦN 3: Single Agent với ReAct

**1. Tìm `create_react_agent()` — đây là magic function**
- Hàm này tự động tạo ra một đồ thị LangGraph đóng vai trò làm tác nhân ReAct (Reasoning + Acting). Nó nhận vào LLM, danh sách tools và System Prompt, từ đó quản lý luồng suy nghĩ và gọi công cụ lặp lại tự động.

**2. So sánh với Stage 2: không còn manual tool loop**
- Ở Stage 2, phải tự viết code kiểm tra xem LLM có gọi tool hay không (`if response.tool_calls`), tự viết vòng lặp gọi hàm và truyền kết quả ngược lại cho LLM. Ở Stage 3, LangGraph tự động hóa toàn bộ vòng lặp đó cho đến khi Agent có câu trả lời cuối cùng.

**3. Xem `agent_executor.invoke()` — chỉ cần gọi một lần**
- Chỉ cần truyền câu hỏi đầu tiên vào `graph.ainvoke()` (hoặc `agent_executor.invoke()`). Toàn bộ quá trình chạy vòng lặp suy nghĩ và gọi các công cụ trung gian đều diễn ra tự động bên dưới và chỉ trả về trạng thái cuối cùng khi kết thúc.

---

### PHẦN 4: Multi-Agent In-Process (Hệ thống Multi-Agent chạy nội bộ)

**1. Tìm `class State(TypedDict)` — đây là shared state**
- `State` định nghĩa cấu trúc dữ liệu chung được lưu truyền qua tất cả các nodes (agents) của đồ thị. Trong Stage 4, nó bao gồm: câu hỏi gốc (`question`), phân tích luật (`law_analysis`), các cờ định tuyến (`needs_tax`, `needs_compliance`), kết quả của agent thuế (`tax_result`) và tuân thủ (`compliance_result`), và cuối cùng là báo cáo hoàn chỉnh (`final_answer`). Các trường kết quả phân tích song song được khai báo reducer `_last_wins` để tránh xung đột ghi đè.

**2. Tìm các agent functions: `law_agent`, `tax_agent`, `compliance_agent`**
- Mỗi hàm này là một node độc lập đại diện cho một AI chuyên môn riêng biệt, nhận vào `State` chung và trả về kết quả phân tích chuyên môn tương ứng dưới dạng cập nhật một trường dữ liệu trong State.

**3. Tìm `Send()` API — dispatch parallel tasks**
- `Send(node, state)` cho phép định tuyến động, phân tách luồng điều khiển của đồ thị để gọi song song các agent chuyên môn (`tax_agent`, `compliance_agent`) dựa trên trạng thái phân tích định tuyến của `check_routing`.

**4. Xem `graph.add_node()` và `graph.add_edge()`**
- `graph.add_node()` được dùng để định nghĩa và đăng ký các node (các agent hoặc hàm xử lý) vào đồ thị.
- `graph.add_edge()` định nghĩa luồng đi cố định, không điều kiện từ node này sang node khác (ví dụ: `START` -> `analyze_law` -> `check_routing`).

---

### PHẦN 5: Distributed A2A System (Hệ thống phân tán)

**Bài Tập 5.1: Trace request flow**
- **Sequence Diagram (Luồng chạy):**
  `Client` -> `Customer Agent` (Port 10100) -> Gửi yêu cầu tìm kiếm lên `Registry` (Port 10000) -> Định tuyến sang `Law Agent` (Port 10101) -> Chạy phân tích pháp lý, định tuyến và gửi song song request sang `Tax Agent` (Port 10102) & `Compliance Agent` (Port 10103) -> Các sub-agent trả về kết quả -> `Law Agent` tổng hợp kết quả -> `Customer Agent` nhận kết quả -> `Client` nhận kết quả cuối cùng.
- **Trace ID:** Mọi A2A request trung gian đều truyền kèm header chứa `trace_id` để liên kết log của toàn bộ hệ thống lại với nhau.

**Bài Tập 5.2: Test fault tolerance**
- **Kết quả:** Hệ thống **không bị sập toàn bộ**. Do hàm `call_tax` trong `Law Agent` được bao bọc trong khối `try-except`, lỗi kết nối tới `Tax Agent` được bắt lại và trả về thông báo lỗi nội bộ `[Tax analysis unavailable...]`. Phân tích pháp lý chung và phân tích tuân thủ (Compliance) vẫn được tổng hợp đầy đủ và trả về bình thường cho người dùng.

**Bài Tập 5.3: Modify agent behavior**
- **Kết quả:** Đã chỉnh sửa system prompt của `tax_agent/graph.py` để hướng dẫn phản hồi ngắn gọn hơn, khởi động lại `tax_agent` và chạy test qua file `test_client.py` để thấy phản hồi chính xác, nhanh hơn.

---

### PHẦN 6: CÂU HỎI ÔN TẬP

**1. Khi nào nên dùng single agent thay vì multi-agent?**
- Nên dùng single agent cho các bài toán đơn giản, thuộc cùng một miền tri thức (single-domain), không yêu cầu chia nhỏ các bước xử lý quá phức tạp hoặc khi muốn tối ưu chi phí và độ trễ phản hồi. Dùng multi-agent khi bài toán lớn, đa miền kiến thức, cần phân công các vai trò chuyên môn sâu hoặc chạy các tác vụ độc lập song song.

**2. Ưu điểm của A2A protocol so với gRPC hoặc REST thông thường?**
- A2A protocol chuẩn hóa cấu trúc gói tin giao tiếp giữa các AI agent (Agent Card, Tasks, Parts) và tích hợp sẵn cơ chế **Trace Propagation** giúp việc debug và giám sát suy nghĩ của AI dễ dàng hơn. Nó hỗ trợ dynamic discovery mặc định thông qua Registry, cho phép các agent tự khám phá ra nhau mà không cần cấu hình định tuyến tĩnh như REST/gRPC.

**3. Làm thế nào để prevent infinite delegation loops trong A2A?**
- Sử dụng cơ chế giới hạn độ sâu ủy quyền (Depth Guard / Max Delegation Depth limit). Trong A2A SDK, mỗi lượt gọi tiếp theo sẽ tăng thuộc tính `depth` lên 1. Nếu `depth` vượt quá một ngưỡng nhất định (ví dụ `MAX_DELEGATION_DEPTH = 3`), request sẽ bị chặn và trả về lỗi ngay lập tức để tránh vòng lặp vô hạn.

**4. Tại sao cần Registry service? Có thể hardcode URLs không?**
- Registry đóng vai trò Service Discovery (Khám phá dịch vụ). Nó cho phép các agent tự động đăng ký cổng/địa chỉ khi khởi chạy và động tìm kiếm địa chỉ của các agent khác. Nếu hardcode URLs, khi có bất kỳ agent nào thay đổi port, host hoặc được scale up lên nhiều instance, ta sẽ phải sửa code và khởi động lại toàn bộ các agent khác. Registry giúp hệ thống có tính linh hoạt và khả năng co giãn (scaling) cao.

**5. Latency và Phương án tối ưu (Bài Tập Cộng Điểm):**
- **Latency trung bình:** Thường từ **30 - 60 giây**, do hệ thống phải thực hiện nhiều lượt gọi LLM liên kết qua lại và độ trễ mạng Internet khi gọi API.
- **Phương án giảm latency:**
  - **Song song hóa tác vụ (Parallel Dispatch):** Đã áp dụng bằng cách dùng LangGraph `Send` để chạy song song `Tax Agent`, `Compliance Agent` và `Privacy Agent` thay vì gọi tuần tự.
  - **Lựa chọn model (Model Selection):** Đổi sang các model nhỏ và nhanh hơn (như `llama-3.1-8b-instant` trên Groq hoặc `gemini-2.0-flash`).
  - **Prompt Caching:** Sử dụng prompt caching của nhà cung cấp API để tăng tốc độ phân tích prompt đầu vào.

---

## PHẦN B: BÁO CÁO KẾT QUẢ THỰC HÀNH CÁC STAGES

### 1. Kết quả chạy thành công Exercise 2 (Tools & Knowledge Base)
- File thực hành: [exercises/exercise_2_tools.py](exercises/exercise_2_tools.py)
- **Log chạy thực tế:**
  ```text
  Câu hỏi: Thời hiệu khởi kiện vụ vi phạm hợp đồng là bao lâu?

  🔧 Gọi tool: check_statute_of_limitations

  ✅ Kết quả:
  Thời hiệu khởi kiện vụ vi phạm hợp đồng là 2 hoặc 4 năm, tùy thuộc vào loại hợp đồng và luật áp dụng. Trong luật thương mại Uniform (UCC), thời hiệu khởi kiện vụ vi phạm hợp đồng mua bán hàng hóa là 4 năm (UCC § 2-725).
  ```

### 2. Kết quả chạy thành công Exercise 4 (Multi-Agent với Privacy Agent)
- File thực hành: [exercises/exercise_4_multiagent.py](exercises/exercise_4_multiagent.py)
- **Sơ đồ đồ thị LangGraph hoàn chỉnh đã tạo:** [exercises/exercise_4_complete_graph.png](exercises/exercise_4_complete_graph.png)
- **Log báo cáo đầu ra của đồ thị Multi-Agent:**
  ```text
  Câu hỏi: Nếu công ty bị rò rỉ dữ liệu khách hàng, hậu quả pháp lý và thuế là gì?
  Đang xử lý qua các agents...

  🎨 Sơ đồ đồ thị Multi-Agent hoàn chỉnh (đã có Privacy Agent) đã được vẽ và lưu tại: 'exercises/exercise_4_complete_graph.png'
  ----------------------------------------------------------------------
  ======================================================================
  KẾT QUẢ CUỐI CÙNG
  ======================================================================
  **BÁO CÁO PHÁP LÝ VÀ THUẾ VỀ HẬU QUẢ CỦA RÒ RÌ DỮ LIỆU KHÁCH HÀNG**
  ... (Báo cáo đầy đủ về Hợp đồng, Trách nhiệm dân sự, Phạt hành chính, Thuế TNDN, uy tín và biện pháp giảm thiểu) ...
  ```

### 3. Kết quả chạy thành công Stage 5 (Distributed A2A System)
- File điều phối: [start_all.ps1](start_all.ps1)
- File client kiểm thử: [test_client.py](test_client.py)
- **Trạng thái khởi chạy của các dịch vụ:**
  - Registry chạy thành công trên cổng `10000`.
  - Tax Agent đăng ký và lắng nghe trên cổng `10102`.
  - Compliance Agent đăng ký và lắng nghe trên cổng `10103`.
  - Law Agent đăng ký và lắng nghe trên cổng `10101`.
  - Customer Agent đăng ký và lắng nghe trên cổng `10100`.
- **Đầu ra E2E từ test client (khi gọi qua API Mistral):**
  Hệ thống xử lý hoàn tất phân tích toàn bộ khía cạnh vi phạm hợp đồng, nghĩa vụ thuế, và phản hồi thành công báo cáo pháp lý tích hợp cho Client từ Customer Agent, đồng thời đã áp dụng thành công prompt ngắn gọn hơn cho Tax Agent (Bài Tập 5.3).
