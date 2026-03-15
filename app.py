import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 및 UI 설정
st.set_page_config(page_title="Steam DNA Analyzer", page_icon="🎮", layout="centered")
st.title("🎮 스팀 게이밍 DNA 분석 대시보드")
st.write("유저의 스팀 라이브러리를 분석하여 게이밍 성향을 시각화합니다.")

# 2. 아이디 입력부 (API 에러를 피하기 위해 UI만 구현)
steam_id = st.text_input("SteamID64를 입력하세요:", "76561198028121353")
analyze_btn = st.button("내 게임 전적 분석하기")

st.divider()

if analyze_btn:
    st.success("✅ 스팀 서버 데이터 연동 완료! (현재 가상 데이터로 시각화 테스트 중)")
    
    # 3. 스팀 API가 정상 작동할 때 받아오게 될 데이터 형태 (가상 데이터)
    mock_data = {
        '게임명': ['Tom Clancy\'s Rainbow Six Siege', 'Cyberpunk 2077', 'ELDEN RING', 'PUBG: BATTLEGROUNDS', 'Grand Theft Auto V', 'Stardew Valley', 'Apex Legends'],
        '플레이타임(시간)': [1250.5, 340.2, 210.8, 850.0, 420.5, 115.3, 530.0],
        '장르': ['FPS', 'RPG', 'RPG', 'FPS', '오픈월드', '시뮬레이션', 'FPS']
    }
    df = pd.DataFrame(mock_data)
    
    # 4. 선웅 님이 기획하신 '전적 분석 그래프' 구현
    st.subheader("📊 내 인생을 갈아 넣은 게임 TOP")
    
    # 가로형 막대 그래프 (플레이타임 순 정렬)
    df_sorted = df.sort_values(by='플레이타임(시간)', ascending=True)
    fig_bar = px.bar(df_sorted, x='플레이타임(시간)', y='게임명', orientation='h', 
                     color='플레이타임(시간)', color_continuous_scale='Turbo',
                     title="게임별 누적 플레이타임")
    st.plotly_chart(fig_bar)
    
    # 5. 게임 장르 DNA (성향 분석)
    st.subheader("🧬 게이밍 성향 (DNA) 분석")
    genre_df = df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
    fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4,
                     title="가장 많이 플레이한 장르 비율")
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie)
    
    # 6. 세부 전적 로그 표
    st.subheader("📑 상세 라이브러리 전적")
    st.dataframe(df.sort_values(by='플레이타임(시간)', ascending=False).reset_index(drop=True))
    
    # 7. 종합 평가 코멘트
    total_hours = df['플레이타임(시간)'].sum()
    st.info(f"💡 당신은 스팀에서 총 **{total_hours:,.1f}시간**을 보냈습니다. FPS 장르에 극도로 특화된 '에임 깎는 장인' 티어입니다.")
