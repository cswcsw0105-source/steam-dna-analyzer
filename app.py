import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam DNA Analyzer", page_icon="🎮", layout="centered")
st.title("🎮 스팀 게이밍 DNA 분석 대시보드")
st.write("유저의 스팀 라이브러리를 분석하여 게이밍 성향과 랭킹을 시각화합니다.")

# 🚨 여기에 반드시 '정상 승인된' 32자리 스팀 API 키를 넣으셔야 합니다!
STEAM_API_KEY = "여기에_정상적인_스팀_API_키를_넣으세요"

steam_id = st.text_input("SteamID64를 입력하세요 (예: 76561197960287930):", "")
analyze_btn = st.button("내 진짜 전적 분석하기")

st.divider()

def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

if analyze_btn:
    if STEAM_API_KEY == "여기에_정상적인_스팀_API_키를_넣으세요" or len(STEAM_API_KEY) != 32:
        st.error("⚠️ 에러: 정상적인 스팀 API 키를 코드에 먼저 입력해 주십시오.")
    elif len(steam_id) != 17 or not steam_id.isdigit():
        st.warning("⚠️ SteamID64는 17자리 숫자여야 합니다.")
    else:
        with st.spinner('스팀 서버에서 데이터를 긁어오는 중입니다...'):
            # 실제 스팀 API 서버로 요청 보내기
            url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "format": "json",
                "include_appinfo": "1" # 게임 이름 데이터 포함
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 401 or response.status_code == 403:
                st.error("🚨 서버 접근 거부: API 키가 유효하지 않거나 권한이 없습니다. 다른 키를 발급받아 주십시오.")
            elif response.status_code == 200:
                data = response.json()
                
                # 프로필이 비공개인 경우 예외 처리
                if not data.get('response') or 'games' not in data['response']:
                    st.error("🔒 이 계정은 스팀 프로필의 '게임 세부 정보'가 비공개 상태입니다. 스팀 설정에서 '공개'로 변경해 주십시오.")
                else:
                    st.success("✅ 스팀 서버 데이터 연동 대성공! 실제 라이브러리를 분석합니다.")
                    
                    # JSON 데이터를 Pandas 데이터프레임으로 변환
                    games = data['response']['games']
                    df = pd.DataFrame(games)
                    
                    # 플레이타임이 0인 게임 제외 및 분 단위를 시간 단위로 변환
                    df = df[df['playtime_forever'] > 0]
                    df['플레이타임(시간)'] = df['playtime_forever'] / 60
                    
                    # 상위 15개 게임만 추출 (데이터가 너무 많으면 그래프가 깨지므로)
                    df_top = df.sort_values(by='플레이타임(시간)', ascending=False).head(15).reset_index(drop=True)
                    df_top['플레이타임'] = df_top['플레이타임(시간)'].apply(format_playtime)
                    df_top['순위'] = [f"{i+1}위" for i in range(len(df_top))]
                    
                    # --- 글로벌 랭킹 추정 로직 ---
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
                
                    # --- 플레이타임 바 차트 ---
                    st.subheader("📊 내 인생을 갈아 넣은 게임 TOP")
                    fig_bar = px.bar(df_top.sort_values(by='플레이타임(시간)', ascending=True), 
                                     x='플레이타임(시간)', y='name', orientation='h', 
                                     color='플레이타임(시간)', color_continuous_scale='Turbo')
                    fig_bar.update_yaxes(title_text="") 
                    fig_bar.update_xaxes(title_text="플레이타임 (시간)")
                    fig_bar.update_traces(text=df_top.sort_values(by='플레이타임(시간)', ascending=True)['플레이타임'], textposition='inside', insidetextanchor='middle')
                    fig_bar.update_layout(height=500)
