import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam Test", page_icon="🎮")
st.title("🎮 스팀 연결 테스트")

# 🚨 여기에 방금 발급받은 32자리 키를 큰따옴표 안에 정확히 넣어!
STEAM_API_KEY = "여기에_너의_스팀_API_키를_넣어" 

steam_id = st.text_input("SteamID64 입력 (따옴표 없이 숫자 17자리만!):", "76561197960287930")

if st.button("분석하기"):
    if len(steam_id) != 17 or not steam_id.isdigit():
        st.warning("⚠️ 입력창에 공백이나 따옴표 빼고 숫자 17자리만 넣어주세요.")
    else:
        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": STEAM_API_KEY,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": "1"
        }
        
        response = requests.get(url, params=params)
        
        # 스팀 서버가 보내준 진짜 응답을 화면에 그대로 출력 (원인 파악용)
        st.write("🔍 스팀 서버의 응답 상태 코드:", response.status_code)
        
        if response.status_code == 403:
            st.error("🚨 403 에러: API 키가 틀렸거나, 권한이 없습니다. 코드 10번째 줄을 다시 확인해!")
        elif response.status_code == 200:
            data = response.json()
            if not data['response'] or 'games' not in data['response']:
                st.error("🔒 스팀 서버랑 연결은 성공했는데, 이 계정이 게임 목록을 '비공개'로 해놨어.")
            else:
                st.success("✅ 통신 대성공! 데이터가 정상적으로 들어왔습니다.")
                df = pd.DataFrame(data['response']['games'])
                df['playtime_hours'] = round(df['playtime_forever'] / 60, 1)
                top_10 = df.sort_values(by='playtime_hours', ascending=False).head(10)
                st.dataframe(top_10[['name', 'playtime_hours']])
        else:
            st.error(f"알 수 없는 에러 발생: {response.text}")
