import streamlit as st
import pandas as pd
from openai import OpenAI
import datetime
import json

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="DeepSeek Spending", page_icon="🐳", layout="wide")

with st.sidebar:
    st.title("⚙️ Cấu hình")
    # Nhập Key DeepSeek tại đây
    ds_key = st.text_input("Nhập DeepSeek API Key", type="password")
    if st.button("Xóa lịch sử"):
        st.session_state.db = pd.DataFrame(columns=['Thời gian', 'Nội dung', 'Hạng mục', 'Số tiền'])
        st.rerun()

# Khởi tạo dữ liệu
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Thời gian', 'Nội dung', 'Hạng mục', 'Số tiền'])

# --- HÀM XỬ LÝ VỚI DEEPSEEK ---
def analyze_with_deepseek(text, key):
    try:
        # Cấu hình trỏ về server của DeepSeek
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
        
        prompt = f"""
        Phân tích câu chi tiêu: "{text}"
        Trả về JSON duy nhất:
        - category: (Ăn uống, Di chuyển, Mua sắm, Giải trí, Khác)
        - amount: (số tiền dạng số nguyên)
        - desc: (nội dung ngắn gọn)
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat", # Hoặc deepseek-reasoner nếu bạn muốn nó suy nghĩ kỹ hơn
            messages=[
                {"role": "system", "content": "Bạn là trợ lý tài chính chỉ trả về JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Lỗi DeepSeek: {e}")
        return None

# --- GIAO DIỆN ---
st.title("🐳 Quản Lý Chi Tiêu với DeepSeek AI")

user_input = st.text_input("Nhập chi tiêu:", placeholder="Ví dụ: Ăn lẩu hết 500k")

if st.button("Phân tích với DeepSeek ✨"):
    if not ds_key:
        st.warning("Vui lòng nhập DeepSeek API Key!")
    elif user_input:
        with st.spinner("DeepSeek đang phân tích..."):
            res = analyze_with_deepseek(user_input, ds_key)
            if res:
                new_row = {
                    'Thời gian': datetime.datetime.now().strftime("%d/%m/%Y"),
                    'Nội dung': res['desc'],
                    'Hạng mục': res['category'],
                    'Số tiền': res['amount']
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Đã thêm: {res['desc']}!")

st.divider()
st.dataframe(st.session_state.db, use_container_width=True)

if not st.session_state.db.empty:
    total = st.session_state.db['Số tiền'].sum()
    st.metric("Tổng cộng", f"{total:,}")
