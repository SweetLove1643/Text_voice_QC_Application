import streamlit as st
from streamlit_tags import st_tags
import json
import requests

webhook_url = "https://n8n.ai.hvnet.vn/webhook-test/6ecf3814-40b0-4340-ba7b-5f61d997b700"
# webhook_url = "https://n8n.ai.hvnet.vn/webhook/6ecf3814-40b0-4340-ba7b-5f61d997b700"


def init_state():
    defaults = {
        "required_keywords": [],
        "forbidden_keywords": [],
        "last_script": "",
        "last_result": None,
        "reload_keyword_forbidden": 0,
        "reload_keyword_required": 0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

def reload_tags():
    st.session_state.reload_keyword_forbidden += 1
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

st.set_page_config(page_title="QC Text Voice", layout="wide")

st.markdown(
    """
    <h1>🔎 Hệ thống QC cho text voice video</h1>
    <p style="color:gray">Thực hiện QC cho text script theo yêu cầu tùy chỉnh.</p>
    <hr>
    """,
    unsafe_allow_html=True,
)

st.subheader("📝 Nhập Script cần QC")

script = st.text_area(
    "Nhập nội dung cần QC",
    height=250,
    placeholder="Nhập nội dung vào đây...",
)

left, right = st.columns([1.1, 1])


with left:
    st.subheader("📚 Rule Base")

    with st.expander("📥 Import Rule Base từ JSON"):
        file_up = st.file_uploader("Chọn file JSON", type=["json"])
        if file_up and st.button("Import & Merge JSON", on_click=reload_tags):
            import_json_rulebase(file_up)

    st.markdown("### 🚫 Forbidden Keywords")
    if st.button("Clear all forbidden", on_click=reload_tags):
        st.session_state["forbidden_keywords"] = []
    forbidden_ui = st_tags(
        label="Thêm từ cấm",
        text="Thêm từ mới...",
        value=st.session_state["forbidden_keywords"],
        key=f"forbidden_tags_{st.session_state.reload_keyword_forbidden}"
    )
    st.markdown("### ✅ Required Keywords")
    if st.button("Clear all required", on_click=reload_tags):
        st.session_state["required_keywords"] = []

    required_ui = st_tags(
        label="Thêm từ bắt buộc",
        text="Thêm từ mới...",
        value=st.session_state["required_keywords"],
        key=f"required_tags_{st.session_state.reload_keyword_required}"
    )

    with st.expander("👀 JSON Rule Base hiện tại"):
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
    st.subheader("🎯 Cấu hình điểm trừ (Score Settings)")

    with st.expander("⚙️ Setup Score Parameters"):
        score_missing_required = st.number_input(
            "Điểm trừ khi thiếu Required Keywords", 
            value=-12, step=1
        )
        score_forbidden_found = st.number_input(
            "Điểm trừ khi có Forbidden Keywords", 
            value=-7, step=1
        )
        score_hook = st.number_input("Điểm trừ thiếu Hook", value=-2, step=1)
        score_solution = st.number_input("Điểm trừ thiếu Solution", value=-2, step=1)
        score_usp = st.number_input("Điểm trừ thiếu USP", value=-2, step=1)
        score_time = st.number_input("Điểm trừ thiếu Time", value=-1, step=1)

        score_mechanism = st.number_input("Điểm trừ thiếu Mechanism", value=-2, step=1)
        score_usage = st.number_input("Điểm trừ thiếu Usage", value=-1, step=1)

        score_testimonial = st.number_input("Điểm trừ thiếu Testimonial", value=-2, step=1)
        score_cta = st.number_input("Điểm trừ thiếu CTA", value=-3, step=1)
        score_promo = st.number_input("Điểm trừ thiếu Promotion", value=-3, step=1)

        score_pass = st.number_input(
            "Điểm tối thiểu để PASS", 
            value=90, step=1
        )

with right:
    st.subheader("⚙️ Tuỳ chọn QC")
    op1, op2 = st.columns(2)
    with op1:
        qc_req = st.checkbox("QC Required Keywords", value=True)
        qc_forb = st.checkbox("QC Forbidden Keywords", value=True)
        qc_solution = st.checkbox("Check Solution", value=True)
        qc_hook = st.checkbox("Check Hook", value=True)
        qc_usp = st.checkbox("Check USP", value=True)
        qc_time = st.checkbox("Check time", value=True)
    with op2: 
        qc_mechanism =st.checkbox("Check Mechanism", value=True)
        qc_usage = st.checkbox("Check usage", value=True)
        qc_testinmonial = st.checkbox("Check Testimonial", value=True)
        qc_cta = st.checkbox("Check CTA", value=True)
        qc_promo = st.checkbox("Check Promotion", value=True)

    st.markdown("---")

    if st.button("▶️ Run QC", use_container_width=True):

        if not script.strip():
            st.warning("⚠️ Vui lòng nhập script.")
            st.stop()

        if not (qc_req or qc_forb or qc_hook or qc_usp or qc_time or qc_mechanism or qc_usage or qc_testinmonial or qc_cta or qc_promo):
            st.warning("⚠️ Hãy bật ít nhất một tuỳ chọn QC.")
            st.stop()

        data_requests = {
            "script": script,  
            "policy_criteria":{
                "required_keywords": [st.session_state["required_keywords"]],
                "forbidden_keywords": [st.session_state["forbidden_keywords"]]
            },
            "content_criteria":{
                "check_hook": qc_hook,
                "check_solution_usp_time":{
                    "check_solution": qc_solution,
                    "check_usp": qc_usp,
                    "check_time": qc_time
                },
                "check_mechanism_usage":{
                    "check_mechanism": qc_mechanism,
                    "check_usage": qc_usage
                },
                "check_testimonial": qc_testinmonial,
                "check_cta_promo": {
                    "check_cta": qc_cta,
                    "check_promotion": qc_promo
                }
            },
            "score": {
                "missing_required_keywords": score_missing_required,
                "forbidden_keywords_found": score_forbidden_found,
                "hook": score_hook,
                "solution": score_solution,
                "usp": score_usp,
                "time": score_time,
                "mechanism": score_mechanism,
                "usage": score_usage,
                "testimonial": score_testimonial,
                "cta": score_cta,
                "promotion": score_promo,
                "pass": score_pass
            }
        }
        res = requests.post(webhook_url, json=json.dumps(data_requests), headers={'Content-Type': 'application/json'})
        raw = res.text
        try:
            parsed = json.loads(raw)
        except:
            parsed = {
                "error": "Invalid JSON in webhook response",
                "raw": raw
            }
        st.session_state["last_result"] = parsed


    st.subheader("📊 Kết quả QC")

    result = st.session_state.get("last_result")

    if not result:
        st.info("⏳ Chưa có dữ liệu.")
        st.stop()

    with st.expander("🔎 JSON trả về từ Webhook"):
        st.json(result)

    is_passed = result.get("is_passed", False)
    score = result.get("score", 0)
    score_req = result.get("score_req", 0)

    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Kết quả", "PASS" if is_passed else "FAIL")
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
            st.metric("Missing Required Keywords", len(missing[0]) if missing else 0)
        with c2:
            st.metric("Forbidden Keywords Found", len(forbidden[0]) if forbidden else 0)

        with st.expander("❗ Missing Required Keywords"):
            if missing and missing[0]:
                st.error(f"• {missing}")
            else:
                st.success("Không thiếu từ bắt buộc.")

        with st.expander("⛔ Forbidden Keywords Found"):
            if forbidden and forbidden[0]:
                st.warning(f"• {forbidden}")
            else:
                st.success("Không phát hiện từ cấm.")

    st.markdown("---")
    content = result.get("content_check", {})

    st.markdown("## 🧩 Content Check")

    with st.expander("ℹ️ Chi tiết Content Check", expanded=False):
        def show_block(title, block):
            exists = block.get("exists", False)
            excerpt = block.get("excerpt", "")

            if exists:
                st.success(f"✔ {title}")
                st.write(excerpt)
            else:
                st.error(f"✘ {title}")

        show_block("Hook", content.get("hook", {}))

        # SOLUTION / USP / TIME`
        sut = content.get("solution_usp_time", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            show_block("Solution", sut.get("solution", {}))
        with col2:
            show_block("USP", sut.get("usp", {}))
        with col3:
            show_block("Time", sut.get("time", {}))

        # MECHANISM / USAGE
        mu = content.get("mechanism_usage", {})
        col4, col5 = st.columns(2)
        with col4:
            show_block("Mechanism", mu.get("mechanism", {}))
        with col5:
            show_block("Usage", mu.get("usage", {}))

        # TESTIMONIAL
        show_block("Testimonial", content.get("testimonial", {}))

        # CTA + PROMOTION
        cta = content.get("cta_promo", {})
        col6, col7 = st.columns(2)
        with col6:
            show_block("CTA", cta.get("cta", {}))
        with col7:
            show_block("Promotion", cta.get("promotion", {}))
