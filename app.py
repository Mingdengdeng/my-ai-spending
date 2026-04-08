import streamlit as st
import pandas as pd
import google.generativeai as genai
import datetime
import json

# --- CẤU HÌNH ---
st.set_page_config(page_title="AI Spending Gemini", page_icon="💎", layout="wide")

with st.sidebar:
    st.title("⚙️ Cấu hình")
    gemini_key = st.text_input("Nhập Gemini API Key", type="password")
    if st.button("Xóa lịch sử"):
        st.session_state.db = pd.DataFrame(columns=['Thời gian', 'Nội dung', 'Hạng mục', 'Số tiền'])
        st.rerun()

# Khởi tạo dữ liệu
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Thời gian', 'Nội dung', 'Hạng mục', 'Số tiền'])

# --- HÀM XỬ LÝ VỚI GEMINI ---
def analyze_with_gemini(text, key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-pro') # Bản flash rất nhanh và miễn phí
        
        prompt = f"""
        Phân tích câu chi tiêu sau: "{text}"
        Trả về JSON duy nhất với:
        - category: (Ăn uống, Di chuyển, Mua sắm, Giải trí, Khác)
        - amount: (số tiền dạng số nguyên)
        - desc: (nội dung ngắn gọn)
        Ví dụ: "Mì tôm 10k" -> {{"category": "Ăn uống", "amount": 10000, "desc": "Mì tôm"}}
        """
        
        response = model.generate_content(prompt)
        # Làm sạch chuỗi trả về để đảm bảo là JSON thuần túy
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Lỗi Gemini: {e}")
        return None

# --- GIAO DIỆN ---
st.title("💎 Quản Lý Chi Tiêu với Gemini AI")

user_input = st.text_input("Nhập chi tiêu của bạn:", placeholder="Ví dụ: Làm quán mì 1000 TWD")

if st.button("Phân tích ✨"):
    if not gemini_key:
        st.warning("Vui lòng nhập API Key từ Google AI Studio!")
    elif user_input:
        with st.spinner("Gemini đang xử lý..."):
            res = analyze_with_gemini(user_input, gemini_key)
            if res:
                new_row = {
                    'Thời gian': datetime.datetime.now().strftime("%d/%m/%Y"),
                    'Nội dung': res['desc'],
                    'Hạng mục': res['category'],
                    'Số tiền': res['amount']
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Đã thêm thành công!")

st.divider()
st.dataframe(st.session_state.db, use_container_width=True)
if not st.session_state.db.empty:
    st.info(f"Tổng cộng: {st.session_state.db['Số tiền'].sum():,} đơn vị tiền tệ")
