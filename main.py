import streamlit as st
from streamlit_tags import st_tags
import json
import requests
from textwrap import dedent

# webhook_url = "https://n8n.ai.hvnet.vn/webhook-test/6ecf3814-40b0-4340-ba7b-5f61d997b700"
webhook_url = "https://n8n.ai.hvnet.vn/webhook/6ecf3814-40b0-4340-ba7b-5f61d997b700"

def init_state():
    defaults = {
        "required_keywords": [
            "Sản phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."
        ],
        "forbidden_keywords": [
            "chữa", "chữa trị", "trị", "điều trị", "đặc trị", "trị liệu",
            "hết bệnh", "hết hẳn", "khỏi hẳn", "khỏi bệnh",
            "dứt điểm", "hết sạch", "sạch bệnh", "diệt bệnh",
            "tận gốc", "sạch gốc", "triệt tiêu", "loại bỏ hoàn toàn",
            "đánh bay", "thổi bay", "xua tan bệnh",
            "vĩnh biệt bệnh", "ngăn ngừa", "phòng ngừa",
            "xóa sổ", "diệt tận gốc", "diệt sạch",
            "thuốc", "bài thuốc", "thần dược",

            "vĩnh viễn", "vĩnh cửu", "mãi mãi", "cả đời",
            "không bao giờ cần đến bác sĩ", "không cần bác sĩ",
            "hiệu quả tức thì", "hiệu quả ngay lập tức", "tác dụng ngay",
            "100% hiệu quả", "hiệu quả tuyệt đối", "không kích ứng 100%",
            "tự nhiên 100%", "nguyên chất 100%", "hữu cơ 100%",
            "thần kỳ", "kỳ diệu", "siêu nhanh", "siêu hiệu quả",

            "99%", "100%", "tỷ lệ thành công",
            "số 1", "top 1", "hàng đầu Việt Nam", "uy tín nhất",
            "được tin dùng bởi hàng triệu người",
            "được khuyên dùng bởi bác sĩ",

            "không gây kích ứng tuyệt đối",
            "không thể thất bại",
            "đảm bảo an toàn tuyệt đối",
            "đảm bảo khỏi bệnh",

            "trị mụn tận gốc",
            "trị nám",
            "điều trị da liễu",
            "đặc trị mụn",
            "điều trị sẹo",

            "thuốc lá", "vape", "thuốc lá điện tử",
            "rượu", "bia", "thức uống có cồn",
            "tình dục", "kích dục", "bao cao su",

            "tôn giáo", "thiên chúa", "phật giáo", "hồi giáo",
            "đảng", "chính phủ", "quốc hội", "nhà nước",
            "bộ trưởng", "lãnh đạo", "cán bộ", "sĩ quan", "quân đội",
            "cựu chiến binh", "cơ quan nhà nước",

            "hành động nguy hiểm", "mạo hiểm",
            "ghê rợn", "kinh dị", "máu me", "bạo lực",
            "gây sốc", "rùng rợn", "đáng sợ",

            "mô tả hành vi nguy hiểm",
            "mô tả gây sốc",
            "tái hiện chấn thương",
            "hình ảnh tiêu cực quá mức"
        ],
        "last_script": "",
        "last_result": None,
        "reload_keyword_forbidden": 0,
        "reload_keyword_required": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

def reload_forbidden():
    st.session_state.forbidden_keywords = []
    st.session_state.reload_keyword_forbidden += 1
def reload_required():
    st.session_state.required_keywords = []
    st.session_state.reload_keyword_required += 1

def merge_keywords(old_list, new_list):
    """Merge 2 list keyword, bỏ trùng."""
    out = list(old_list)
    for x in new_list:
        if x not in out:
            out.append(x)
    return out

def import_json_rulebase(uploaded_file):
    """Import JSON và merge vào session_state + cập nhật UI."""
    try:
        data = json.load(uploaded_file)

        req = data.get("required_keywords", [])
        forb = data.get("forbidden_keywords", [])

        required_keywords_new = merge_keywords(
            st.session_state["required_keywords"], req
        )
        st.session_state["required_keywords"] = required_keywords_new

        forbidden_keywords_new = merge_keywords(
            st.session_state["forbidden_keywords"], forb
        )
        st.session_state["forbidden_keywords"] = forbidden_keywords_new
        
        st.success("✅ Import & merge JSON thành công!")

    except Exception as e:
        st.error(f"❌ Lỗi khi đọc JSON: {e}")

st.set_page_config(page_title="QC Text Voice", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
      .app-hero{
        text-align:center;
        padding: 18px 16px 14px 16px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,.12);
        background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.02));
        box-shadow: 0 10px 30px rgba(0,0,0,.12);
        margin-bottom: 14px;
      }
      .app-title{
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: .2px;
        background: linear-gradient(90deg, #7dd3fc, #a78bfa, #fb7185);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
      }
      .app-sub{
        margin: 6px 0 0 0;
        color: rgba(255,255,255,.70);
        font-size: 1.02rem;
      }
      .app-badge{
        display:inline-block;
        margin-top: 10px;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.14);
        background: rgba(255,255,255,.06);
        font-size: .85rem;
        color: rgba(255,255,255,.75);
      }
      .app-hr{
        height:1px;
        border:none;
        margin: 14px auto 0 auto;
        width: 68%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.22), transparent);
      }
    </style>

    <div class="app-hero">
      <h1 class="app-title">🔎 Hệ thống QC cho text voice video</h1>
      <p class="app-sub">Thực hiện QC cho text script theo yêu cầu tùy chỉnh.</p>
      <div class="app-badge">✨ QC • Script • Voice • Video</div>
      <hr class="app-hr"/>
    </div>
    """,
    unsafe_allow_html=True,
)

if "show_help" not in st.session_state:
    st.session_state.show_help = False
@st.dialog("📘 Hướng dẫn sử dụng")
def help_dialog():
    st.markdown("""
## 📌 Mô tả ứng dụng
Ứng dụng này dùng để **kiểm duyệt (QC) nội dung kịch bản (voice video)** trước khi tạo **Video AI**, theo các chuẩn nội dung **AIDA** hoặc **PAS**.

## 🧩 Ứng dụng kiểm tra được gì?
- **Từ cấm**: phát hiện các từ/ cụm từ không được xuất hiện trong kịch bản
- **Từ bắt buộc**: kiểm tra kịch bản có chứa các từ/ cụm từ cần phải có hay không
- **Chuẩn nội dung AIDA / PAS**: đánh giá nội dung dựa trên các thành phần đã tách (ví dụ: *Hook, Problem/Solution, Time, ...*)
  - Hỗ trợ cơ chế **Optional**: một số thành phần có thể “không bắt buộc” phải kiểm tra
- **Chấm điểm kịch bản**: cho điểm tổng quan và **chỉ ra phần còn thiếu / chưa đạt**
- **Kiểm tra cấu trúc**: kiểm tra bố cục kịch bản có đúng cấu trúc chuẩn hay không

---

## ✅ Cách sử dụng (Quickstart)
> Lưu ý: Ứng dụng có **mục bắt buộc** và **mục không bắt buộc** (nếu chưa cần, bạn có thể bỏ qua).

1. **Nhập kịch bản**  
   Dán toàn bộ nội dung *voice script* vào ô **“Kịch bản”** để chuẩn bị kiểm tra.

2. **(Tuỳ chọn) Nhập từ cấm / từ bắt buộc**  
   Thêm danh sách **từ cấm** hoặc **từ bắt buộc** nếu bạn muốn kiểm tra theo rule riêng.

3. **Chọn chuẩn nội dung**  
   Chọn **AIDA** hoặc **PAS** (mặc định là **AIDA**) trong phần **Tùy chọn QC nâng cao**.

4. **Chạy QC và xem kết quả**  
   Bấm **QC** để nhận báo cáo: lỗi từ cấm, thiếu từ bắt buộc, thiếu thành phần, điểm số và gợi ý cải thiện.

---

## ⚙️ Tuỳ chỉnh nâng cao (tuỳ chọn)
Bạn có thể điều chỉnh cơ chế kiểm tra để phù hợp từng chiến dịch, ví dụ:
- **Nhập thông tin sản phẩm** để hệ thống kiểm tra bám sát sản phẩm hơn
- **Định nghĩa lại tiêu chí định tính** cho từng thành phần trong mẫu nội dung (Hook, Solution, ...)
- **Điều chỉnh cơ chế trừ điểm** để thay đổi mức độ “gắt” khi chấm điểm
""")
    if st.button("Đóng"):
        st.session_state.show_help = False
        st.rerun()
if st.button("📘 Hướng dẫn"):
    st.session_state.show_help = True
if st.session_state.show_help == True:
    help_dialog()

st.subheader("📝 Nhập Kịch bản cần kiểm tra")

script = st.text_area(
    "Nhập nội dung cần kiểm tra",
    height=250,
    placeholder="Nhập nội dung vào đây..."
)

left, right = st.columns([1, 1])

with left:  
    st.subheader("📚 Cấu hình kiểm tra")

    with st.expander("📥 Nhập từ danh sách từ cấm/bắt buộc bằng file JSON"):
        file_up = st.file_uploader("Chọn file JSON", type=["json"])
        if file_up and st.button("Import & Merge JSON", on_click=reload_tags):
            import_json_rulebase(file_up)

    with st.expander("📄 Hiện tại Rule Base", expanded = True):
        st.markdown("### 🚫 Danh sách từ cấm")
        st.button("Xóa danh sách từ cấm", on_click=reload_forbidden)
        forbidden_ui = st_tags(
            label="Thêm từ cấm",
            text="Thêm từ mới...",
            value=st.session_state["forbidden_keywords"],
            key=f"forbidden_tags_{st.session_state.reload_keyword_forbidden}"
        )
        st.session_state.forbidden_keywords = forbidden_ui

        st.markdown("### ✅ Danh sách từ bắt buộc")
        st.button("Xóa danh sách từ bắt buộc", on_click=reload_required)
        required_ui = st_tags(
            label="Thêm từ bắt buộc",
            text="Thêm từ mới...",
            value=st.session_state["required_keywords"],
            key=f"required_tags_{st.session_state.reload_keyword_required}"
        )
        st.session_state.required_keywords = required_ui 

    with st.expander("👀 JSON danh sách từ cấm hiện tại"):
        current_json = {
            "required_keywords": st.session_state["required_keywords"],
            "forbidden_keywords": st.session_state["forbidden_keywords"],
        }

        st.json(current_json)

        json_str = json.dumps(current_json, indent=2, ensure_ascii=False)

        st.download_button(
            label="⬇️ Tải xuống JSON",
            data=json_str,
            file_name="rules_base.json",
            mime="application/json"
        )

    with st.expander("🛍️ Thông tin sản phẩm"):
        info = st.text_area(
            "📝 Nhập / dán thông tin sản phẩm",
            placeholder="VD: Tên, mô tả, giá, thành phần, link ảnh, tồn kho...",
            height=220,
        )   

    with st.expander("⚙️ Tuỳ chọn QC nâng cao"):
        st.subheader("⚙️ Tuỳ chọn QC")
        qc_req = st.checkbox("Kiểm tra các từ bắt buộc", value=True)
        qc_forb = st.checkbox("Kiểm tra các từ cấm", value=True)
        
        active = st.radio(
            "QC theo mẫu nội dung:",
            ["AIDA", "PAS"],
            horizontal=True,
            key="active_tab"
        )
        if active == "AIDA":
            st.subheader("📄 Checklist AIDA")

            cA, cI, cD, cA2 = st.columns(4)

            with cA:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Attention</h4>', unsafe_allow_html=True)
                    qc_aida_hook = st.checkbox("Kiểm tra Hook", value=True, key="qc_aida_hook")

            with cI:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Interest</h4>', unsafe_allow_html=True)
                    qc_aida_solution  = st.checkbox("Kiểm tra Solution", value=True, key="qc_aida_solution")
                    qc_aida_usp  = st.checkbox("Kiểm tra USP", value=True, key="qc_aida_usp")
                    qc_aida_time = st.checkbox("Kiểm tra Time", value=True, key="qc_aida_time")

            with cD:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Desire</h4>', unsafe_allow_html=True)
                    qc_aida_mechanism = st.checkbox("Kiểm tra Mechanism", value=True, key="qc_aida_mechanism")
                    qc_aida_testimonial = st.checkbox("Kiểm tra Testimonial", value=True, key="qc_aida_testimonial")
                    qc_aida_usage       = st.checkbox("Kiểm tra Usage", value=True, key="qc_aida_usage")

            with cA2:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Action</h4>', unsafe_allow_html=True)
                    qc_aida_cta  = st.checkbox("Kiểm tra CTA", value=True, key="qc_aida_cta")
                    qc_aida_promo = st.checkbox("Kiểm tra Promotion", value=True, key="qc_aida_promo")

        elif active == "PAS":
            st.subheader("📄 Checklist PAS")

            cP, cA, cS = st.columns(3)

            with cP:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Problem</h4>', unsafe_allow_html=True)
                    qc_pas_hook = st.checkbox("Kiểm tra Hook", value=True, key="qc_pas_hook")
                    qc_pas_problem_statement = st.checkbox("Kiểm tra Problem Statement", value=True, key="qc_pas_problem_statement")

            with cA:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Agitate</h4>', unsafe_allow_html=True)
                    qc_pas_agitate = st.checkbox("Kiểm tra Agitate", value=True, key="qc_pas_agitate")
                    qc_pas_antisolution = st.checkbox("Kiểm tra Anti-solution", value=True, key="qc_pas_antisolution")

            with cS:
                with st.container(border=True):
                    st.markdown('<h4 style="margin:0; color:#ff4b4b; font-weight:600;">Solution</h4>', unsafe_allow_html=True)
                    qc_pas_solution = st.checkbox("Kiểm tra Solution", value=True, key="qc_pas_solution")
                    qc_pas_usp = st.checkbox("Kiểm tra USP", value=True, key="qc_pas_usp")
                    qc_pas_time = st.checkbox("Kiểm tra Time", value=True, key="qc_pas_time")
                    qc_pas_mechanism   = st.checkbox("Kiểm tra Mechanism", value=True, key="qc_pas_mechanism")
                    qc_pas_usage   = st.checkbox("Kiểm tra Usage", value=True, key="qc_pas_usage")
                    qc_pas_proof_testimonial = st.checkbox("Kiểm tra Proof/Testimonial", value=True, key="qc_pas_proof_testimonial")
                    qc_pas_cta     = st.checkbox("Kiểm tra CTA", value=True, key="qc_pas_cta")
                    qc_pas_promotion     = st.checkbox("Kiểm tra Promotion", value=True, key="qc_pas_promotion")

    with st.expander("📄 Định nghĩa các mẫu nội dung (Content Templates)"):
        if active == "AIDA":
            st.subheader("📄 Mẫu nội dung AIDA")
            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Attention</h5>', unsafe_allow_html=True)
            define_hook_aida = st.text_input("Định nghĩa Hook", 
                                             value = "Là câu nói chặn lướt, thu hút người xem, thường đặt vấn đề hoặc “gọi tên tình trạng” để kéo người xem vào AIDA")

            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Interest</h5>', unsafe_allow_html=True)
            define_solution_aida = st.text_input("Định nghĩa Solution", 
                                                 value = "Là câu giới thiệu sản phẩm, đưa ra cách giải quyết vấn đề của khách hàng nhờ vào sản phẩm")
            define_usp_aida = st.text_input("Định nghĩa Unique Selling Point", 
                                            value = "Là câu nêu điểm đặc biệt của sản phẩm đang giới thiệu so với các sản phẩm khác ngoài thị trường, khiến cho khách hàng chọn sản phẩm của mình vì điểm khác biệt đó")
            define_time_aida = st.text_input("Định nghĩa Time Effect", 
                                             value = "Là câu đề cập thời gian cụ thể giờ, ngày, tháng,... mà người dùng có thể bắt đầu cảm thấy sự tác động/cải thiện vấn đề của mình do sản phẩm ảnh hưởng tới")
            
            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Desire</h5>', unsafe_allow_html=True)
            define_mechanism_aida = st.text_input("Định nghĩa Mechanism", 
                                                  value = "Là câu giải thích ngắn gọn cơ chế, vì sao giải pháp/sản phẩm này có thể giải quyết vấn đề hoặc giải thích cách tác động của thành phần sản phẩm tới vấn đề mà người dùng đang gặp phải.")
            define_usage_aida = st.text_input("Định nghĩa Usage", 
                                              value="Là câu hướng dẫn cơ bản dành cho người dùng cách sử dụng sản phẩm như thế nào")
            define_testimonial_aida = st.text_input("Định nghĩa Testimonial", 
                                                    value="Là câu bằng chứng xã hội từ người dùng thật (feedback/quote/case) giúp tăng niềm tin, thường có 3 ý: trước khi dùng – trải nghiệm – kết quả/cảm nhận. ")
            
            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Action</h5>', unsafe_allow_html=True)
            define_cta_aida = st.text_input("Định nghĩa Call to action", 
                                            value="Là lời kêu gọi hành động rõ việc cần làm ngay (nhắn tin, bấm link, điền form…).")
            define_promotion_aida = st.text_input("Định nghĩa Promotion", 
                                                  value="Là câu lý do để hành động sớm (ưu đãi/quà tặng/freeship/combo/thời hạn).")
        if active == "PAS":
            st.subheader("📄 Mẫu nội dung PAS")
            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Problem</h5>', unsafe_allow_html=True)
            define_hook_pas = st.text_input("Định nghĩa Hook", value = "Là câu nói chặn lướt, thu hút người xem, thường đặt vấn đề hoặc “gọi tên tình trạng” để kéo người xem vào PAS")
            define_problem_statement_pas = st.text_input("Định nghĩa Problem Statement", value = "Là câu nêu vấn đề cụ thể, mô tả triệu chứng/tình huống thật rõ, đúng tệp, càng cụ thể càng tốt để người xem tự gật đầu “đúng tôi rồi”.")
            
            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Agitate</h5>', unsafe_allow_html=True)
            define_agitate_pas = st.text_input("Định nghĩa Agitate", value = "Là câu nói đề cập đến những nỗi đau, bất tiện, khó chịu mà người dùng phải chịu nếu không sử dụng sản phẩm/dịch vụ.")
            define_antisolution_pas = st.text_input("Định nghĩa Anti-solution", value = "Là câu nói về việc khách hàng đang sử dụng giải pháp A nhưng không hiệu quả, từ đó tạo tiền đề giới thiệu giải pháp B (sản phẩm của đang giới thiệu).")

            st.markdown('<h5 style="margin:0; color:#ff4b4b; font-weight:300;">Solution</h5>', unsafe_allow_html=True)
            define_solution_pas = st.text_input("Định nghĩa Solution", value="Là câu giới thiệu sản phẩm, đưa ra cách giải quyết vấn đề của khách hàng nhờ vào sản phẩm")
            define_usp_pas = st.text_input("Định nghĩa Unique Selling Point", value="Là câu nêu điểm đặc biệt của sản phẩm đang giới thiệu so với các sản phẩm khác ngoài thị trường, khiến cho khách hàng chọn sản phẩm của mình vì điểm khác biệt đó")
            define_time_pas = st.text_input("Định nghĩa Time Effect", value="Là câu đề cập thời gian cụ thể giờ, ngày, tháng,... mà người dùng có thể bắt đầu cảm thấy sự tác động/cải thiện vấn đề của mình do sản phẩm ảnh hưởng tới")

            define_mechanism_pas = st.text_input("Định nghĩa Mechanism", value="Là câu giải thích cách sản phẩm hoặc các thành phần của sản phẩm có thể giải quyết vấn về của khác hàng theo logic đơn giản")
            define_usage_pas = st.text_input("Định nghĩa Usage", value="Là câu hướng dẫn cơ bản dành cho người dùng cách sử dụng sản phẩm như thế nào")

            define_proof_testimonial_pas = st.text_input("Định nghĩa Proof/Testimonial", value = "Là câu bằng chứng xã hội từ người dùng thật (feedback/quote/case) giúp tăng niềm tin, thường có 3 ý: trước khi dùng – trải nghiệm – kết quả/cảm nhận.")

            define_cta_pas = st.text_input("Định nghĩa Call to action", value="Là lời kêu gọi hành động rõ việc cần làm ngay (nhắn tin, bấm link, điền form…)")
            define_promotion_pas = st.text_input("Định nghĩa Promotion", value="Là câu lý do để hành động sớm (ưu đãi/quà tặng/freeship/combo/thời hạn).")

with right:
    st.subheader("🎯 Cấu hình điểm trừ")
    with st.expander("⚙️ Cài đặt các điểm trừ cho từng mục QC"):
        score_missing_required = st.number_input(
            "Điểm trừ khi thiếu Required Keywords", 
            value=-12, step=1
        )
        score_forbidden_found = st.number_input(
            "Điểm trừ khi có Forbidden Keywords", 
            value=-7, step=1
        )
        
        if active == "AIDA":
            st.markdown("#### Cấu hình điểm trừ cho AIDA")
            aida_score_hook = st.number_input("Điểm trừ thiếu Hook", value=-2, step=1)

            aida_score_solution = st.number_input("Điểm trừ thiếu Solution", value=-2, step=1)
            aida_score_usp = st.number_input("Điểm trừ thiếu USP", value=-2, step=1)
            aida_score_time = st.number_input("Điểm trừ thiếu Time", value=-1, step=1)

            aida_score_mechanism = st.number_input("Điểm trừ thiếu Mechanism", value=-2, step=1)
            aida_score_usage = st.number_input("Điểm trừ thiếu Usage", value=-1, step=1)
            aida_score_testimonial = st.number_input("Điểm trừ thiếu Testimonial", value=-2, step=1)

            aida_score_cta = st.number_input("Điểm trừ thiếu CTA", value=-3, step=1)
            aida_score_promo = st.number_input("Điểm trừ thiếu Promotion", value=-3, step=1)

        elif active == "PAS":
            st.markdown("#### Cấu hình điểm trừ cho PAS")
            pas_hook = st.number_input("Điểm trừ thiếu Hook", value=-2, step=1)
            pas_problem_statement = st.number_input("Điểm trừ thiếu Problem Statement", value=-3, step=1)
            
            pas_agitate = st.number_input("Điểm trừ thiếu Agitate", value=-3, step=1)
            pas_anti_solution = st.number_input("Điểm trừ thiếu Anti-solution", value=-2, step=1)

            pas_solution = st.number_input("Điểm trừ thiếu Solution", value=-2, step=1)
            pas_usp = st.number_input("Điểm trừ thiếu Usp", value=-2, step=1)
            pas_time = st.number_input("Điểm trừ thiếu Time", value=-1, step=1)

            pas_mechanism = st.number_input("Điểm trừ thiếu Mechanism", value=-3, step=1)
            pas_usage = st.number_input("Điểm trừ thiếu Usage", value=-3, step=1)

            pas_proof_testimonial = st.number_input("Điểm trừ thiếu Proof/Testimonial", value=-4, step=1)

            pas_cta = st.number_input("Điểm trừ thiếu CTA", value=-4, step=1)   
            pas_promotion = st.number_input("Điểm trừ thiếu Promotion", value=-4, step=1)   
        score_pass = st.number_input("Điểm tối thiểu để PASS", value=90, step=1, min_value=0, max_value=100)
     
    st.markdown("---")

    st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"]{
            background: #2563EB;      /* màu nền */
            color: white;             /* màu chữ */
            border: 1px solid #2563EB;
            border-radius: 10px;
            height: 44px;
            font-weight: 600;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover{
            filter: brightness(1.05);
        }
        </style>
        """, unsafe_allow_html=True)

    if st.button("▶️ Bắt đầu kiểm tra", use_container_width=True, type="primary", key="run_qc"):
        if not script.strip():
            st.warning("⚠️ Vui lòng nhập script.")
            st.stop()

        if info:
            prompt_info = f"""4. Đây là thông tin chính xác về sản phẩm mà người dùng cung cấp, có thể dựa vào đây để tiến hành kiểm định:{info}"""
        else:
            prompt_info = "" 

        if active == "AIDA":
            if not (qc_req 
                    or qc_forb 
                    or qc_aida_hook 
                    or qc_aida_solution 
                    or qc_aida_usp 
                    or qc_aida_time 
                    or qc_aida_mechanism 
                    or qc_aida_usage 
                    or qc_aida_testimonial 
                    or qc_aida_cta 
                    or qc_aida_promo):
                st.warning("⚠️ Hãy bật ít nhất một tuỳ chọn QC.")
                st.stop()
            else:
                payload = {
                                "script": f"{script}",  
                                "policy_criteria":{
                                    "required_keywords": [st.session_state["required_keywords"]],
                                    "forbidden_keywords": [st.session_state["forbidden_keywords"]]
                                },                                
                            }
                                
                output_format = {
                                "policy_criteria":{
                                    "required_keywords": [],
                                    "forbidden_keywords": []
                                },
                                "content_criteria":{
                                    "check_attention":{
                                        "check_hook": { "exists": False, "excerpt": "" }
                                    },
                                    "check_interest":{
                                        "check_solution": { "exists": False, "excerpt": "" },
                                        "check_usp": { "exists": False, "excerpt": "" },
                                        "check_time": { "exists": False, "excerpt": "" }
                                    },
                                    "check_desire":{
                                        "check_mechanism": { "exists": False, "excerpt": "" },
                                        "check_usage": { "exists": False, "excerpt": "" },
                                        "check_testimonial": { "exists": False, "excerpt": "" }
                                    },
                                    "check_action":{
                                        "check_cta": { "exists": False, "excerpt": "" },
                                        "check_promotion": { "exists": False, "excerpt": "" }
                                    }
                                },
                                "structure": {
                                    "is_valid_structure": False,
                                    "issues": ""
                                }
                            }
                
                prompt = f"""
                        Bạn là một chuyên viên chuyên kiểm tra nội dung lời thoại video theo chuẩn AIDA.
                        Nhiệm vụ của bạn là kiểm định cho đoạn script dưới đây dựa trên các tiêu chí mà người dùng gửi vào.
                            1. Đây là nội dung bạn cần kiểm tra
                            {payload}
                            2. CÁCH THỨC KIỂM TRA
                            2.1 Chính sách 
                            - required_keywords: kiểm tra xem các keywords có tồn tài trong script hay không và trả về những từ bị thiếu.
                            - forbidden_keywords: Trả về các keywords bị cấm xuất hiện trong script.
                            2.2 Content Criteria
                            Ở mỗi phần hãy trả về exists: true/false và excerpt (xác định CHÍNH XÁC và trích dẫn lại các văn đoạn (nếu có)) 
                            Nếu excerpt có nhiều hơn một thì hãy liên kết bằng cách kí tự liên kết(ví dụ như ||) để làm sao nhận ra đó là nhiều câu nhưng TUYỆT ĐỐI trường "excerpt" không được chứa nhiều chuỗi và chỉ chứa một chuỗi duy nhất
                            Nhiệm vụ của bạn là sẽ kiểm tra script dựa vào các định nghĩa định tính được mô tả như sau:
                            2.2.1 Attention
                            Hook: {define_hook_aida}
                            *Ví dụ: Bạn cũng từng thử đủ cách mà vấn đề này vẫn quay lại y như cũ?
                            2.2.2 Interest
                            Solution: {define_solution_aida}
                            USP: {define_usp_aida}
                            Time: {define_time_aida}
                            *Ví dụ: Giải pháp là [tên sản phẩm/dịch vụ], nổi bật ở [USP], và nhiều người thường bắt đầu cảm nhận [lợi ích] sau khoảng [X ngày/tuần].
                            2.2.3 Desire
                            Mechanism: {define_mechanism_aida}
                            Usage: {define_usage_aida}
                            *Ví dụ: Cơ chế là [cơ chế] giúp [tác động], và bạn chỉ cần dùng [liều/cách] vào [thời điểm] mỗi ngày.
                            Testimonial: {define_testimonial_aida}
                            *Ví dụ: Chị N. chia sẻ: ‘Trước đây mình [vấn đề], dùng [X thời gian] thì thấy [cải thiện], cảm giác [dễ chịu/tự tin] hẳn.
                            2.2.4 Action
                            Call to action: {define_cta_aida}
                            Promotion: {define_promotion_aida}
                            *Ví dụ: Nhắn ‘TƯ VẤN’ để nhận hướng dẫn phù hợp, đang có ưu đãi [X%/quà] đến hết [ngày/khung giờ].
                            2.3 Cấu trúc
                            Bạn sẽ kiểm tra cấu trúc tổng thể của script có đúng theo mấu AIDA hay không(lần lượt trong script là Attention, Interest, Desire, Action) và trả kết quả is_valid_structure và nêu vấn đề của script bằng tiếng Việt ở issues.
                            3. Định dạng phải trả về (BẮT BUỘC)
                            Luôn trả về JSON hợp lệ theo đúng mẫu sau:
                            {output_format}                           
                            Trả về excerpt = "" thay vì excerpt = null hoặc N/A.
                            Không được trả về thêm bất kỳ nội dung nào ngoài JSON.
                            {prompt_info}
                            YÊU CẦU KIỂM TRA KHẮT KHE, CHÍNH XÁC VỀ SỰ TỒN TẠI CỦA CÁC THUỘC TÍNH TRONG CONTENT CRITERIA DỰA VÀO CÁC ĐỊNH NGHĨA Ở TRÊN.
                        """
                
                data_requests = {
                    "starndard": "AIDA",
                    "prompt": f"{prompt}",
                    "settings": {
                            "check_required_keywords": qc_req,
                            "check_forbidden_keywords": qc_forb,
                            "check_attention":{
                                "check_hook": qc_aida_hook
                            },
                            "check_interest":{
                                "check_solution": qc_aida_solution,
                                "check_usp": qc_aida_usp,
                                "check_time": qc_aida_time
                            },
                            "check_desire":{
                                "check_mechanism": qc_aida_mechanism,
                                "check_usage": qc_aida_usage,
                                "check_testimonial": qc_aida_testimonial
                            },
                            "check_action":{
                                "check_cta": qc_aida_cta,
                                "check_promotion": qc_aida_promo
                            }
                    },
                    "score": {
                        "missing_required_keywords": score_missing_required,
                        "forbidden_keywords_found": score_forbidden_found,
                        "attention":{
                            "hook": aida_score_hook
                        },
                        "interest": {
                            "solution": aida_score_solution,
                            "usp": aida_score_usp,
                            "time": aida_score_time
                        },
                        "desire": {
                            "mechanism": aida_score_mechanism,
                            "usage": aida_score_usage,
                            "testimonial": aida_score_testimonial
                        },
                        "action": {
                            "cta": aida_score_cta,
                            "promotion": aida_score_promo
                        },
                        "pass": score_pass
                    }
                }
       
        elif active == "PAS":
            if not (qc_req 
                    or qc_forb 
                    or qc_pas_hook 
                    or qc_pas_problem_statement 
                    or qc_pas_agitate 
                    or qc_pas_antisolution 
                    or qc_pas_solution 
                    or qc_pas_usp
                    or qc_pas_time
                    or qc_pas_mechanism 
                    or qc_pas_usage
                    or qc_pas_proof_testimonial 
                    or qc_pas_cta
                    or qc_pas_promotion):
                st.warning("⚠️ Hãy bật ít nhất một tuỳ chọn QC.")
                st.stop()
            else:
                payload = {
                                "script": f"{script}",  
                                "policy_criteria":{
                                    "required_keywords": [st.session_state["required_keywords"]],
                                    "forbidden_keywords": [st.session_state["forbidden_keywords"]]
                                },                                
                            }

                output_format = {
                                "policy_criteria":{
                                    "required_keywords": [],
                                    "forbidden_keywords": []
                                },
                                "content_criteria":{
                                    "check_problem":{
                                        "check_hook": { "exists": False, "excerpt": "" },
                                        "check_problem_statement": { "exists": False, "excerpt": "" }
                                    },
                                    "check_agitate":{
                                        "check_agitate": { "exists": False, "excerpt": "" },
                                        "check_anti_solution": { "exists": False, "excerpt": "" }
                                    },
                                    "check_solution":{
                                        "check_solution": { "exists": False, "excerpt": "" },
                                        "check_usp": { "exists": False, "excerpt": "" },
                                        "check_time": { "exists": False, "excerpt": "" },
                                        "check_mechanism": { "exists": False, "excerpt": "" },
                                        "check_usage": { "exists": False, "excerpt": "" },
                                        "check_proof_testimonial": { "exists": False, "excerpt": "" },
                                        "check_cta": { "exists": False, "excerpt": "" },
                                        "check_promotion": { "exists": False, "excerpt": "" }
                                    }
                                },
                                "structure": {
                                    "is_valid_structure": False,
                                    "issues": ""
                                }
                            }
                
                prompt = f"""
                        Bạn là một chuyên viên chuyên kiểm tra nội dung lời thoại video theo chuẩn PAS.
                        Nhiệm vụ của bạn là kiểm định cho đoạn script dưới đây dựa trên các tiêu chí mà người dùng gửi vào.
                            1. Đây là nội dung bạn cần kiểm tra
                            {payload}
                            2. CÁCH THỨC KIỂM TRA
                            2.1 Chính sách 
                            - required_keywords: kiểm tra xem các keywords có tồn tài trong script hay không và trả về những từ bị thiếu.
                            - forbidden_keywords: Trả về các keywords bị cấm xuất hiện trong script.
                            2.2 Content Criteria
                            Ở mỗi phần hãy trả về exists: true/false và excerpt (xác định CHÍNH XÁC và trích dẫn lại các văn đoạn (nếu có))
                            Nếu excerpt có nhiều hơn một thì hãy liên kết bằng cách kí tự liên kết(ví dụ như ||) để làm sao nhận ra đó là nhiều câu nhưng TUYỆT ĐỐI trường "excerpt" không được chứa nhiều chuỗi và chỉ chứa một chuỗi duy nhất
                            Nhiệm vụ của bạn là sẽ kiểm tra script dựa vào các định nghĩa định tính được mô tả như sau:
                            2.2.1 Problem
                            Hook: {define_hook_pas}
                            *Ví dụ: Nếu bạn đang [vấn đề] mà càng làm càng không cải thiện, bạn không hề cô đơn
                            Problem Statement: {define_problem_statement_pas}
                            *Ví dụ: Mỗi lần [tình huống], bạn lại bị [triệu chứng] khiến [bất tiện cụ thể].
                            2.2.2 Agitate
                            Agitate: {define_agitate_pas}
                            *Ví dụ: Cái khó chịu nhất là bạn vừa tốn [tiền/thời gian], vừa mất [tự tin/hiệu suất], mà vẫn phải chịu đi chịu lại.
                            An-ti Solution: {define_antisolution_pas}
                            *Ví dụ: Nhiều người cứ tiếp tục [cách A], nhưng càng làm vậy lại càng khiến [vấn đề] dai hơn.
                            2.2.3 Solution
                            Solution: {define_solution_pas}
                            USP: {define_usp_pas}
                            Time: {define_time_pas}
                            *Ví dụ: Cách phù hợp hơn là [tên giải pháp], khác ở [USP], và thường bạn có thể bắt đầu cảm nhận [lợi ích] sau khoảng [X ngày/tuần].
                            Mechanism: {define_mechanism_pas}
                            Usage: {define_usage_pas}
                            *Ví dụ: Nó hoạt động bằng cách [cơ chế] để [tác động], và bạn chỉ cần [cách dùng] mỗi ngày.
                            Proof/Testimonial: {define_proof_testimonial_pas}  
                            *Ví dụ: Bạn K. phản hồi: ‘Mình [vấn đề] lâu, dùng [X thời gian] thì thấy [cải thiện], dễ chịu hơn rõ.
                            CTA: {define_cta_pas}
                            Promotion: {define_promotion_pas}
                            *Ví dụ: Nhắn ‘NHẬN TƯ VẤN’ để mình hướng dẫn đúng trường hợp của bạn—ưu đãi [X%/quà] đến hết [mốc thời gian].
                            2.3 Cấu trúc
                            Bạn sẽ kiểm tra cấu trúc tổng thể của script có đúng theo mấu PAS hay không(lần lượt trong script là Problem, Agitate, Solution) và trả kết quả is_valid_structure và nêu vấn đề của script bằng tiếng Việt ở issues.
                            3. Định dạng phải trả về (BẮT BUỘC)
                            Luôn trả về JSON hợp lệ theo đúng mẫu sau:
                            {output_format}                           
                            Trả về excerpt = "" thay vì excerpt = null hoặc N/A.
                            Không được trả về thêm bất kỳ nội dung nào ngoài JSON.
                            {prompt_info}
                            YÊU CẦU KIỂM TRA KHẮT KHE, CHÍNH XÁC VỀ SỰ TỒN TẠI CỦA CÁC THUỘC TÍNH TRONG CONTENT CRITERIA DỰA VÀO CÁC ĐỊNH NGHĨA Ở TRÊN.
                        """

                data_requests = {
                    "starndard": "PAS",
                    "prompt": f"{prompt}", 
                    "settings":{
                        "check_required_keywords": qc_req,
                        "check_forbidden_keywords": qc_forb,
                        "check_problem": {
                            "check_hook": qc_pas_hook,
                            "check_problem_statement": qc_pas_problem_statement
                        },
                        "check_agitate": {
                            "check_agitate": qc_pas_agitate,
                            "check_anti_solution": qc_pas_antisolution
                        },
                        "check_solution": {
                            "check_solution": qc_pas_solution,
                            "check_usp": qc_pas_usp,
                            "check_time": qc_pas_time,
                            "check_mechanism": qc_pas_mechanism,
                            "check_usage": qc_pas_usage,
                            "check_proof_testimonial": qc_pas_proof_testimonial,
                            "check_cta": qc_pas_cta,
                            "check_promotion": qc_pas_promotion
                        }
                    },
                    "score": {
                        "missing_required_keywords": score_missing_required,
                        "forbidden_keywords_found": score_forbidden_found,
                        "problem": {
                            "hook": pas_hook,
                            "problem_statement": pas_problem_statement
                        },
                        "agitate": {
                            "agitate": pas_agitate,
                            "anti_solution": pas_anti_solution
                        },
                        "solution": {
                            "solution": pas_solution,
                            "usp": pas_usp,
                            "time": pas_time,
                            "mechanism": pas_mechanism,
                            "usage": pas_usage,
                            "proof_testimonial": pas_proof_testimonial,
                            "cta": pas_cta,
                            "promotion": pas_promotion
                        },
                        "pass": score_pass
                    }
                }
        
        res = requests.post(webhook_url, json=json.dumps(data_requests), headers={'Content-Type': 'application/json'}, timeout=180)
        raw = res.text
        try:
            parsed = json.loads(raw)
        except:
            parsed = {
                "error": "Invalid JSON in webhook response",
                "raw": raw
            }
        st.session_state["last_result"] = parsed

    st.subheader("📊 Kết quả kiểm tra")

    result = st.session_state.get("last_result")

    if not result:
        st.info("⏳ Chưa có dữ liệu.")
        st.stop()

    with st.expander("🔎 JSON trả về từ Webhook"):
        st.json(result)
    if result.get("starndard") == "AIDA":
        is_passed = result.get("is_passed", False)
        score = result.get("score", 0)
        score_req = result.get("score_req", 0)

        colA, colB, colC = st.columns(3)
        with colA:
            label = "Kết quả"
            text = "PASS" if is_passed else "FAIL"
            color = "#16A34A" if is_passed else "#DC2626" 

            st.markdown(
                f"""
                <div style="border: 1px solid rgba(49,51,63,0.2); padding: 12px; border-radius: 10px;">
                <div style="font-size: 0.85rem; color: rgba(255,255,255,0.85); margin-bottom: 6px;">{label}</div>
                <div style="font-size: 1.9rem; font-weight: 1200; color: {color}; line-height: 1;">{text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with colB:
            st.metric("Điểm đạt được", score)
        with colC:
            st.metric("Điểm yêu cầu", score_req)

        st.markdown("---")
        policy = result.get("policy_check", {})

        missing = policy.get("missing_required_keywords", [])
        forbidden = policy.get("forbidden_keywords_found", [])

        st.markdown("## 🛡 Policy Check")
        with st.expander("ℹ️ Chi tiết Policy Check", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Số lượng các từ bắt buộc bị thiếu", len(missing[0]) if missing else 0)
            with c2:
                st.metric("Số lượng các từ cấm được tìm thấy", len(forbidden[0]) if forbidden else 0)

            with st.expander("❗ Danh sách các từ bắt buộc bị thiếu"):
                if missing and missing[0]:
                    st.error(f"• {missing}")
                else:
                    st.success("Không thiếu từ bắt buộc.")

            with st.expander("⛔ Danh sách các từ cấm được tìm thấy"):
                if forbidden and forbidden[0]:
                    st.warning(f"• {forbidden}")
                else:
                    st.success("Không phát hiện từ cấm.")

        st.markdown("---")
        content = result.get("content_criteria", {})

        st.markdown("## 🧩 Content Check")

        with st.expander("ℹ️ Chi tiết Content Check", expanded=False):
            def show_block(title, block):
                exists = block.get("exists", False)
                excerpt = block.get("excerpt", "")

                if exists == "true":
                    st.success(f"✔ {title}")
                    st.write(excerpt)
                else:
                    st.error(f"✘ {title}")
            # Attention
            st.subheader("Attention")
            att = content.get("check_attention", [])
            show_block("Hook", att.get("check_hook", {}))

            # Interest
            st.subheader("Interest")
            inter = content.get("check_interest", {})
            col1, col2, col3 = st.columns(3)
            with col1:
                show_block("Solution", inter.get("check_solution", {}))
            with col2:
                show_block("USP", inter.get("check_usp", {}))
            with col3:
                show_block("Time", inter.get("check_time", {}))

            # Desire
            st.subheader("Desire")
            des = content.get("check_desire", {})
            col4, col5, col6 = st.columns(3)
            with col4:
                show_block("Mechanism", des.get("check_mechanism", {}))
            with col5:
                show_block("Usage", des.get("check_usage", {}))
            with col6:
                show_block("Testimonial", des.get("check_testimonial", {}))

            # Action
            st.subheader("Action")
            act = content.get("check_action", {})
            col7, col8 = st.columns(2)
            with col7:
                show_block("CTA", act.get("check_cta", {}))
            with col8:
                show_block("Promotion", act.get("check_promotion", {}))
        
        st.markdown("## 🧱 Kiểm tra cấu trúc")

        structure = result.get("structure", {}) or {}
        is_valid_structure = str(structure.get("is_valid_structure", False)).strip().lower() == "true"
        issues = (structure.get("issues") or "").strip()

        badge = "✅ Đã hợp lệ" if is_valid_structure else "❌ Chưa hợp lệ"
        st.metric("Kết quả kiểm tra cấu trúc", badge)

        with st.expander("🧱 Chi tiết vấn đề về cấu trúc", expanded=not is_valid_structure):
            if is_valid_structure and not issues:
                st.success("Cấu trúc AIDA hợp lệ. Không có vấn đề.")
            else:
                st.warning("Phát hiện vấn đề về cấu trúc:")
                st.write(issues if issues else "Không có mô tả vấn đề.")
    elif result.get("starndard") == "PAS":
        is_passed = result.get("is_passed", False)
        score = result.get("score", 0)
        score_req = result.get("score_req", 0)

        colA, colB, colC = st.columns(3)
        with colA:
            # st.metric("Kết quả", "PASS" if is_passed else "FAIL")
            label = "Kết quả"
            text = "PASS" if is_passed else "FAIL"
            color = "#16A34A" if is_passed else "#DC2626"  

            st.markdown(
                f"""
                <div style="border: 1px solid rgba(49,51,63,0.2); padding: 12px; border-radius: 10px;">
                <div style="font-size: 0.85rem; color: rgba(255,255,255,0.85); margin-bottom: 6px;">{label}</div>
                <div style="font-size: 1.9rem; font-weight: 1200; color: {color}; line-height: 1;">{text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with colB:
            st.metric("Điểm đạt được", score)
        with colC:
            st.metric("Điểm yêu cầu", score_req)

        st.markdown("---")
        policy = result.get("policy_check", {})

        missing = policy.get("missing_required_keywords", [])
        forbidden = policy.get("forbidden_keywords_found", [])

        st.markdown("## 🛡 Policy Check")
        with st.expander("ℹ️ Chi tiết Policy Check", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Số lượng các từ bắt buộc bị thiếu   ", len(missing[0]) if missing else 0)
            with c2:
                st.metric("Số lượng các từ cấm được tìm thấy", len(forbidden[0]) if forbidden else 0)

            with st.expander("❗ Danh sách các từ bắt buộc bị thiếu"):
                if missing and missing[0]:
                    st.error(f"• {missing}")
                else:
                    st.success("Không thiếu từ bắt buộc.")

            with st.expander("⛔ Danh sách các từ cấm được tìm thấy"):
                if forbidden and forbidden[0]:
                    st.warning(f"• {forbidden}")
                else:
                    st.success("Không phát hiện từ cấm.")

        st.markdown("---")
        content = result.get("content_criteria", {})

        st.markdown("## 🧩 Content Check")

        with st.expander("ℹ️ Chi tiết Content Check", expanded=False):
            def show_block(title, block):
                exists = block.get("exists", False)
                excerpt = block.get("excerpt", "")

                if exists == "true":
                    st.success(f"✔ {title}")
                    st.write(excerpt)
                else:
                    st.error(f"✘ {title}")
            problem = content.get("problem")
            agitate = content.get("agitate")
            solution = content.get("solution")
                        
            st.subheader("Problem")
            pro1, pro2 = st.columns(2)
            with pro1:
                show_block("Hook", problem.get("hook", {}))
            with pro2:
                show_block("Problem Statement", problem.get("problem_statement", {}))

            st.subheader("Agitate")
            agi1, agi2 = st.columns(2)
            with agi1:
                show_block("Agitate", agitate.get("agitate", {}))
            with agi2:
                show_block("Anti Solution", agitate.get("anti_solution", {}))

            st.subheader("Solution")
            sol1, sol2, sol3, sol4 = st.columns(4)
            with sol1:
                show_block("Solution", solution.get("solution", {}))
                show_block("USP", solution.get("usp", {}))
                show_block("Time", solution.get("time", {}))
            with sol2:
                show_block("Mechanism", solution.get("mechanism", {}))
                show_block("Usage", solution.get("usage", {}))
            with sol3:
                show_block("Proof/Testimonial", solution.get("proof_testimonial", {}))
            with sol4:
                show_block("CTA", solution.get("cta", {}))
                show_block("Promotion", solution.get("promotion", {}))
        
        st.markdown("## 🧱 Kiểm tra cấu trúc")

        structure = result.get("structure", {}) or {}
        is_valid_structure = str(structure.get("is_valid_structure", False)).strip().lower() == "true"
        issues = (structure.get("issues") or "").strip()

        badge = "✅ Đã hợp lệ" if is_valid_structure else "❌ Chưa hợp lệ"
        st.metric("Kết quả kiểm tra cấu trúc", badge)

        with st.expander("🧱 Chi tiết vấn đề về cấu trúc", expanded=not is_valid_structure):
            if is_valid_structure and not issues:
                st.success("Cấu trúc AIDA hợp lệ. Không có vấn đề.")
            else:
                st.warning("Phát hiện vấn đề về cấu trúc:")
                st.write(issues if issues else "Không có mô tả vấn đề.")