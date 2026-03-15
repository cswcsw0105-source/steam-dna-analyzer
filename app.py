import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam DNA Analyzer", page_icon="🎮", layout="centered")
st.title("🎮 스팀 게이밍 DNA 분석 대시보드")
st.write("유저의 스팀 라이브러리를 분석하여 게이밍 성향을 시각화합니다.")

steam_id = st.text_input("SteamID64를 입력하세요:", "76561198028121353")
analyze_btn = st.button("내 게임 전적 분석하기")

st.divider()

# --- 헬퍼 함수: 소수점 시간을 'X시간 Y분'으로 변환 ---
def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

if analyze_btn:
    st.success("✅ 스팀 서버 데이터 연동 완료! (현재 가상 데이터 테스트 중)")
    
    # 가상 데이터
    mock_data = {
        '게임명': ['Tom Clancy\'s Rainbow Six Siege', 'Cyberpunk 2077', 'ELDEN RING', 'PUBG: BATTLEGROUNDS', 'Grand Theft Auto V', 'Stardew Valley', 'Apex Legends'],
        '플레이타임(시간)': [1250.5, 340.2, 210.8, 850.0, 420.5, 115.3, 530.0],
        '장르': ['FPS', 'RPG', 'RPG', 'FPS', '오픈월드', '시뮬레이션', 'FPS']
    }
    df = pd.DataFrame(mock_data)
    df['표기용_시간'] = df['플레이타임(시간)'].apply(format_playtime)
    
    # --- 1. 티어(랭크) 및 종합 코멘트 시스템 로직 ---
    total_hours = df['플레이타임(시간)'].sum()
    top_genre = df.groupby('장르')['플레이타임(시간)'].sum().idxmax()
    
    # 총 플레이타임 기반 티어 산정
    if total_hours >= 3000: tier, color = "🏆 스팀의 망령 (Grandmaster)", "#FFD700"
    elif total_hours >= 1500: tier, color = "💎 겜창인생 (Diamond)", "#00BFFF"
    elif total_hours >= 500: tier, color = "🥇 훌륭한 게이머 (Gold)", "#00FA9A"
    else: tier, color = "🌱 응애 뉴비 (Bronze)", "#CD7F32"
    
    # 1순위 장르 기반 코멘트
    genre_comments = {
        'FPS': "당신의 혈관엔 화약이 흐릅니다. 0.1초의 반응속도에 목숨을 거는 '에임 깎는 장인'이시군요.",
        'RPG': "현실의 팍팍함보다 판타지 세계의 모험을 사랑하는 '진정한 낭만파 모험가'입니다.",
        '오픈월드': "정해진 길을 거부하고 나만의 길을 개척하는 '자유로운 영혼'의 소유자입니다.",
        '시뮬레이션': "세상을 내 손으로 통제하고 만들어가는 '창조주'의 마인드를 가졌습니다."
    }
    comment = genre_comments.get(top_genre, "다양한 세계를 탐험하는 올라운더 게이머입니다.")

    # 결과 출력
    st.markdown(f"### 랭크: <span style='color:{color}'>{tier}</span>", unsafe_allow_html=True)
    st.info(f"💡 **총 {total_hours:,.0f}시간** 플레이! {comment}")

    st.divider()
    
    # --- 2. 플레이타임 바 차트 (시간/분 표기 및 가독성 개선) ---
    st.subheader("📊 내 인생을 갈아 넣은 게임 TOP")
    df_sorted = df.sort_values(by='플레이타임(시간)', ascending=True)
    
    fig_bar = px.bar(df_sorted, x='플레이타임(시간)', y='게임명', orientation='h', 
                     color='플레이타임(시간)', color_continuous_scale='Turbo')
    
    # 세로로 누운 '게임명' 라벨 아예 제거 (어차피 게임 이름이라 직관적임)
    fig_bar.update_yaxes(title_text="") 
    fig_bar.update_xaxes(title_text="플레이타임 (시간)")
    
    # 툴팁(마우스 올렸을 때)과 그래프 내부에 'X시간 Y분'으로 표기
    fig_bar.update_traces(
        text=df_sorted['표기용_시간'],
        textposition='inside',
        insidetextanchor='middle',
        hovertemplate="<b>%{y}</b><br>플레이타임: %{text}<extra></extra>"
    )
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # --- 3. 게이밍 성향(DNA) 파이 차트 (가독성 극대화) ---
    st.subheader("🧬 게이밍 성향 (DNA) 분석")
    genre_df = df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
    
    fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4)
    
    # 글씨 굵게, 흰색 바탕에 까만 테두리 느낌으로 가독성 폭발시킴
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(size=16, color='white', family="Arial Black"),
        insidetextorientation='horizontal', # 글씨가 눕지 않고 무조건 가로로 유지되게!
        marker=dict(line=dict(color='#000000', width=2)) # 테두리 추가
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- 4. 상세 로그 ---
    st.subheader("📑 상세 라이브러리 전적")
    st.dataframe(df_sorted.sort_values(by='플레이타임(시간)', ascending=False)[['게임명', '장르', '표기용_시간']].reset_index(drop=True))
