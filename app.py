import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam DNA & Battle", page_icon="🔥", layout="wide")

# 🚨 네 진짜 스팀 API 키를 여기에 넣어!
STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"

# --- 1. 장르 맵핑 사전 (우회 꼼수) ---
# 유명 게임들의 장르를 미리 매핑해둠 (여기에 없는 건 '기타'로 분류됨)
GENRE_MAP = {
    "Tom Clancy's Rainbow Six Siege": "FPS", "PUBG: BATTLEGROUNDS": "FPS", 
    "Apex Legends": "FPS", "Counter-Strike 2": "FPS", "Overwatch 2": "FPS",
    "Grand Theft Auto V": "오픈월드", "Cyberpunk 2077": "RPG", "ELDEN RING": "RPG",
    "Stardew Valley": "시뮬레이션", "Dota 2": "AOS", "Rust": "생존"
}

def get_steam_data(steam_id):
    """스팀 서버에서 데이터를 긁어와서 데이터프레임으로 만들어주는 핵심 엔진"""
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {"key": STEAM_API_KEY, "steamid": steam_id, "format": "json", "include_appinfo": "1"}
    resp = requests.get(url, params=params)
    if resp.status_code != 200: return None
    data = resp.json()
    if not data.get('response') or 'games' not in data['response']: return None
    
    df = pd.DataFrame(data['response']['games'])
    df = df[df['playtime_forever'] > 0]
    df['플레이타임(시간)'] = df['playtime_forever'] / 60
    # 장르 부활 로직!
    df['장르'] = df['name'].apply(lambda x: GENRE_MAP.get(x, '기타 장르'))
    return df.sort_values(by='플레이타임(시간)', ascending=False).reset_index(drop=True)

# --- 2. 메인 UI 구성 ---
st.title("🔥 스팀 게이밍 DNA & 전적 배틀")

col_search1, col_search2 = st.columns(2)
with col_search1:
    my_id = st.text_input("👑 내 SteamID64 (필수):", "76561198028121353")
with col_search2:
    friend_id = st.text_input("⚔️ 친구 SteamID64 (배틀용, 선택):", "")

if st.button("전적 분석 & 배틀 시작!"):
    with st.spinner('서버에서 데이터를 불러오는 중...'):
        my_df = get_steam_data(my_id)
        
        if my_df is None:
            st.error("내 계정 데이터를 불러올 수 없습니다. 프로필 공개 여부나 ID를 확인하세요.")
        else:
            # --- [기능 1] 인스타 박제용 요약 카드 ---
            st.divider()
            st.subheader("📸 Instagram 공유용 요약 카드")
            my_total_hours = my_df['플레이타임(시간)'].sum()
            my_top_game = my_df.iloc[0]['name']
            top_genre = my_df.groupby('장르')['플레이타임(시간)'].sum().idxmax()
            
            # 인스타 스토리 느낌의 컨테이너 박스
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("총 갈아넣은 시간", f"{my_total_hours:,.0f} 시간")
                c2.metric("인생 최고의 게임", my_top_game)
                c3.metric("나의 게이밍 성향", f"{top_genre} 마스터")
                st.caption("✨ 캡처해서 인스타 스토리에 올려보세요! #SteamDNA #인생전적")

            # --- [기능 2] 부활한 장르 DNA 파이 차트 ---
            st.subheader("🧬 나의 게이밍 장르 DNA")
            genre_df = my_df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
            fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', 
                                  textfont=dict(size=14, color='white'), marker=dict(line=dict(color='#000000', width=1)))
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- [기능 3] 친구와의 영혼의 맞다이 (배틀 모드) ---
            if friend_id:
                st.divider()
                st.header("⚔️ 전적 맞다이: 나 vs 친구")
                friend_df = get_steam_data(friend_id)
                
                if friend_df is None:
                    st.warning("친구 계정이 비공개이거나 데이터를 불러올 수 없습니다.")
                else:
                    friend_total = friend_df['플레이타임(시간)'].sum()
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        st.subheader("👑 내 전적")
                        st.metric("총 플레이타임", f"{my_total_hours:,.0f} 시간")
                        st.dataframe(my_df[['name', '플레이타임(시간)']].head(5), use_container_width=True)
                    with b2:
                        st.subheader("⚔️ 상대방 전적")
                        # 이겼는지 졌는지 색깔로 띄워주기
                        delta_val = friend_total - my_total_hours
                        st.metric("총 플레이타임", f"{friend_total:,.0f} 시간", delta=f"나와의 차이: {delta_val:,.0f}시간", delta_color="inverse")
                        st.dataframe(friend_df[['name', '플레이타임(시간)']].head(5), use_container_width=True)
            else:
                st.info("💡 팁: 친구의 SteamID를 입력하면 전적 비교 배틀이 가능합니다!")
                
            # 기본 막대 그래프 (하단 배치)
            st.divider()
            st.subheader("📊 전체 라이브러리 (상위 15개)")
            fig_bar = px.bar(my_df.head(15).sort_values(by='플레이타임(시간)', ascending=True), 
                             x='플레이타임(시간)', y='name', orientation='h', color='플레이타임(시간)')
            fig_bar.update_yaxes(title_text="")
            st.plotly_chart(fig_bar, use_container_width=True)
