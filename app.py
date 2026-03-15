import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="Steam DNA Analyzer", page_icon="🎮")
st.title("🎮 스팀 게이밍 DNA 분석기")

# 1. API 키 설정 (선웅이가 나중에 발급받아서 여기에 넣어야 해!)
STEAM_API_KEY = "여기에_너의_스팀_API_키를_넣어"

st.write("당신의 스팀 플레이타임을 분석해 드립니다.")

# 2. 스팀 ID 입력받기 (실제 서비스에선 '스팀 로그인' 버튼으로 대체할 부분)
# 테스트용 스팀 ID: 76561197960434622 (스팀 창립자 게이브 뉴웰 계정 등 공개된 계정 번호)
steam_id = st.text_input("SteamID64를 입력하세요 (17자리 숫자):", "76561198028121353")

# 데이터 가져오기 버튼
if st.button("내 게임 전적 분석하기"):
    if STEAM_API_KEY == "여기에_너의_스팀_API_키를_넣어":
        st.error("⚠️ 에러: 스팀 API 키를 먼저 입력해야 작동합니다!")
    elif len(steam_id) != 17:
        st.warning("⚠️ SteamID64는 17자리 숫자여야 합니다.")
    else:
        # 3. 스팀 API 찌르기 (보유 게임 목록 & 플레이타임 가져오기)
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": STEAM_API_KEY,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": "1" # 게임 이름이랑 로고 이미지도 같이 줘!
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 4. '비공개' 계정 처리 로직 (이게 아까 말한 그 현실적인 벽이야)
            if not data['response'] or 'games' not in data['response']:
                st.error("🔒 이 계정은 프로필의 '게임 세부 정보'가 비공개 상태입니다. 스팀 설정에서 '공개'로 변경해 주세요.")
            else:
                games = data['response']['games']
                total_games = data['response']['game_count']
                
                # 데이터를 보기 좋게 판다스 데이터프레임으로 변환
                df = pd.DataFrame(games)
                
                # playtime_forever는 '분' 단위야. 이걸 '시간' 단위로 바꾸자.
                df['playtime_hours'] = round(df['playtime_forever'] / 60, 1)
                
                # 플레이타임 순으로 내림차순 정렬 후 상위 10개만 뽑기
                top_10 = df.sort_values(by='playtime_hours', ascending=False).head(10)
                
                st.success(f"✅ 데이터 수집 완료! 총 {total_games}개의 게임을 보유 중입니다.")
                
                # 5. 선웅이가 좋아하는 그래프 그리기!
                st.subheader("📊 내 인생을 갈아 넣은 게임 TOP 10")
                fig = px.bar(top_10, x='playtime_hours', y='name', orientation='h', 
                             title="플레이타임 (시간)", color='playtime_hours',
                             color_continuous_scale='Viridis')
                fig.update_layout(yaxis={'categoryorder':'total ascending'}) # 플레이타임 많은 게 위로 가게 정렬
                st.plotly_chart(fig)
                
                # 표 데이터로도 보여주기
                st.subheader("📑 상세 데이터")
                st.dataframe(top_10[['name', 'playtime_hours']])
                
        except Exception as e:
            st.error(f"통신 중 오류가 발생했습니다: {e}")
