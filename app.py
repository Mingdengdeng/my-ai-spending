import streamlit as st
import pandas as pd
from openai import OpenAI
import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="AI Finance Pro", page_icon="💰", layout="wide")

# Tùy chỉnh giao diện bằng CSS (làm cho giao diện "mượt" hơn)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- KHỞI TẠO BỘ NHỚ (SESSION STATE) ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Thời gian', 'Nội dung', 'Hạng mục', 'Số tiền'])

# --- THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Cấu hình")
    api_key = st.text_input("Nhập OpenAI API Key", type="password")
    st.info("AI sẽ tự động phân tích câu nói của bạn thành dữ liệu.")
    
    if st.button("Xóa lịch sử chi tiêu"):
        st.session_state.db = pd.DataFrame(columns=['Thời gian', 'Nội dung', 'Hạng mục', 'Số tiền'])
        st.rerun()

# --- HÀM XỬ LÝ AI ---
def analyze_spending(text, key):
    client = OpenAI(api_key=key)
    prompt = f"""
    Bạn là một trợ lý tài chính. Phân tích câu: "{text}"
    Trả về JSON với các trường:
    - category: (Ăn uống, Di chuyển, Mua sắm, Giải trí, Tiền điện/nước, Khác)
    - amount: (số tiền dạng số nguyên)
    - desc: (nội dung ngắn gọn)
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Lỗi AI: {e}")
        return None

# --- GIAO DIỆN CHÍNH ---
st.title("💰 Trợ Lý Quản Lý Chi Tiêu AI")

# Khu vực nhập liệu
col_in, col_stat = st.columns([2, 1])

with col_in:
    st.subheader("📝 Nhập chi tiêu")
    user_input = st.text_input("Gõ câu gì đó (VD: Sáng nay ăn phở 45k, đi grab hết 30 ngàn...)", placeholder="Hôm nay bạn đã chi gì?")
    btn_add = st.button("Tự động phân tích & Thêm ✨")

    if btn_add:
        if not api_key:
            st.error("Vui lòng nhập API Key ở thanh bên!")
        elif user_input:
            with st.spinner("AI đang tính toán..."):
                res = analyze_spending(user_input, api_key)
                if res:
                    new_data = {
                        'Thời gian': datetime.datetime.now().strftime("%H:%M - %d/%m/%Y"),
                        'Nội dung': res['desc'],
                        'Hạng mục': res['category'],
                        'Số tiền': res['amount']
                    }
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_data])], ignore_index=True)
                    st.success(f"Đã thêm: {res['desc']} - {res['amount']:,}đ")

with col_stat:
    st.subheader("📊 Tổng quan")
    total = st.session_state.db['Số tiền'].sum()
    st.metric("Tổng chi tiêu", f"{total:,} VNĐ")
    st.write(f"Số giao dịch: {len(st.session_state.db)}")

# Khu vực hiển thị bảng và biểu đồ
st.divider()
tab1, tab2 = st.tabs(["📜 Nhật ký chi tiết", "📈 Biểu đồ phân tích"])

with tab1:
    st.dataframe(st.session_state.db, use_container_width=True)

with tab2:
    if not st.session_state.db.empty:
        chart_data = st.session_state.db.groupby('Hạng mục')['Số tiền'].sum()
        st.bar_chart(chart_data)
        st.pie_chart(chart_data)
    else:
        st.write("Chưa có dữ liệu để vẽ biểu đồ.")