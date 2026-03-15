import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.set_page_config(page_title="Steam DNA Analyzer", page_icon="🎮", layout="centered")
st.title("🎮 스팀 게이밍 DNA 분석 대시보드")
st.write("유저의 스팀 라이브러리를 분석하여 게이밍 성향과 랭킹을 시각화합니다.")

steam_id = st.text_input("SteamID64를 입력하세요:", "76561198028121353")
analyze_btn = st.button("내 게임 전적 분석하기")

st.divider()

def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

if analyze_btn:
    st.success("✅ 스팀 서버 데이터 연동 완료! (현재 가상 데이터 테스트 중)")
    
    mock_data = {
        '게임명': ['Tom Clancy\'s Rainbow Six Siege', 'Cyberpunk 2077', 'ELDEN RING', 'PUBG: BATTLEGROUNDS', 'Grand Theft Auto V', 'Stardew Valley', 'Apex Legends'],
        '플레이타임(시간)': [1250.5, 340.2, 210.8, 850.0, 420.5, 115.3, 530.0],
        '장르': ['FPS', 'RPG', 'RPG', 'FPS', '오픈월드', '시뮬레이션', 'FPS']
    }
    df = pd.DataFrame(mock_data)
    
    # 1위부터 정렬하기 위해 미리 정렬
    df_sorted = df.sort_values(by='플레이타임(시간)', ascending=False).reset_index(drop=True)
    
    # 시간 포맷팅
    df_sorted['플레이타임'] = df_sorted['플레이타임(시간)'].apply(format_playtime)
    
    # --- 1. [NEW] 순위 컬럼 추가 (1위, 2위...) ---
    df_sorted['순위'] = [f"{i+1}위" for i in range(len(df_sorted))]
    
    # --- 2. [NEW] 글로벌 상위 % 추정 로직 (프로토타입용 가상 공식) ---
    total_hours = df['플레이타임(시간)'].sum()
    
    # 예시: 3000시간 이상이면 상위 0.1%, 1000시간이면 5% 등 자체 공식
    estimated_top_percent = max(0.01, 100 - (total_hours / 35)) 
    
    st.markdown(f"### 🏆 당신의 스팀 글로벌 랭킹 (추정)")
    
    # 스트림릿 컬럼으로 멋지게 수치 띄우기
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="총 플레이타임", value=f"{total_hours:,.0f} 시간")
    with col2:
        st.metric(label="글로벌 상위", value=f"Top {estimated_top_percent:.2f}%", delta="상위권 진입!")
    with col3:
        st.metric(label="대한민국 랭킹", value=f"약 {int(estimated_top_percent * 15000):,} 위") # 가상의 등수 공식

    st.divider()

    # --- 그래프 (이전과 동일하게 유지) ---
    st.subheader("📊 내 인생을 갈아 넣은 게임 TOP")
    fig_bar = px.bar(df_sorted.sort_values(by='플레이타임(시간)', ascending=True), 
                     x='플레이타임(시간)', y='게임명', orientation='h', 
                     color='플레이타임(시간)', color_continuous_scale='Turbo')
    fig_bar.update_yaxes(title_text="") 
    fig_bar.update_xaxes(title_text="플레이타임 (시간)")
    fig_bar.update_traces(text=df_sorted.sort_values(by='플레이타임(시간)', ascending=True)['플레이타임'], textposition='inside', insidetextanchor='middle')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # --- 3. [NEW] 깔끔해진 상세 라이브러리 전적 표 ---
    st.subheader("📑 상세 라이브러리 전적")
    
    # 보여줄 컬럼만 선택하고, '순위'를 인덱스로 설정해서 0, 1, 2 지워버리기
    display_df = df_sorted[['순위', '게임명', '장르', '플레이타임']].set_index('순위')
    
    # 스트림릿 내장 dataframe 함수로 깔끔하게 출력
    st.dataframe(display_df, use_container_width=True)
