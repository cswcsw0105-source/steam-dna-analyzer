import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam DNA Analyzer", page_icon="🎮", layout="centered")
st.title("🎮 스팀 게이밍 DNA 분석 대시보드")
st.write("유저의 스팀 라이브러리를 분석하여 게이밍 성향과 랭킹을 시각화합니다.")

# 선웅이가 뚫어낸 진짜 마스터 키 적용 완료!
STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"

steam_id = st.text_input("SteamID64를 입력하세요 (예: 76561198028121353):", "")
analyze_btn = st.button("내 진짜 전적 분석하기")

st.divider()

def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

if analyze_btn:
    if len(steam_id) != 17 or not steam_id.isdigit():
        st.warning("⚠️ SteamID64는 17자리 숫자여야 합니다.")
    else:
        with st.spinner('스팀 서버에서 진짜 데이터를 긁어오는 중입니다...'):
            url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "format": "json",
                "include_appinfo": "1" 
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('response') or 'games' not in data['response']:
                    st.error("🔒 이 계정은 스팀 프로필이 비공개 상태입니다. (공개된 아이디로 테스트해 보세요!)")
                else:
                    st.success("✅ 스팀 서버 데이터 연동 대성공! 실제 라이브러리를 분석합니다.")
                    
                    games = data['response']['games']
                    df = pd.DataFrame(games)
                    
                    # 플레이타임이 0인 게임 제외 및 분 -> 시간 변환
                    df = df[df['playtime_forever'] > 0]
                    df['플레이타임(시간)'] = df['playtime_forever'] / 60
                    
                    # 상위 15개 게임 추출
                    df_top = df.sort_values(by='플레이타임(시간)', ascending=False).head(15).reset_index(drop=True)
                    df_top['플레이타임'] = df_top['플레이타임(시간)'].apply(format_playtime)
                    df_top['순위'] = [f"{i+1}위" for i in range(len(df_top))]
                    
                    # 글로벌 랭킹 추정
                    total_hours = df['플레이타임(시간)'].sum()
                    estimated_top_percent = max(0.01, 100 - (total_hours / 50))
                    
                    st.markdown(f"### 🏆 당신의 스팀 글로벌 랭킹 (추정)")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="총 플레이타임", value=f"{total_hours:,.0f} 시간")
                    with col2:
                        st.metric(label="글로벌 상위", value=f"Top {estimated_top_percent:.2f}%", delta="상위권 진입!")
                    with col3:
                        st.metric(label="보유 게임 수", value=f"{len(df):,} 개")
                
                    st.divider()
                
                    # 그래프 그리기
                    st.subheader("📊 내 인생을 갈아 넣은 게임 TOP")
                    fig_bar = px.bar(df_top.sort_values(by='플레이타임(시간)', ascending=True), 
                                     x='플레이타임(시간)', y='name', orientation='h', 
                                     color='플레이타임(시간)', color_continuous_scale='Turbo')
                    fig_bar.update_yaxes(title_text="") 
                    fig_bar.update_xaxes(title_text="플레이타임 (시간)")
                    fig_bar.update_traces(text=df_top.sort_values(by='
