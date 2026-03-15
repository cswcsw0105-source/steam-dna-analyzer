import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam DNA & Battle", page_icon="🔥", layout="wide")

# 🚨 API 키 확인!
STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"

GENRE_MAP = {
    "Tom Clancy's Rainbow Six Siege": "FPS", "PUBG: BATTLEGROUNDS": "FPS", 
    "Apex Legends": "FPS", "Counter-Strike 2": "FPS", "Overwatch 2": "FPS",
    "Grand Theft Auto V": "오픈월드", "Cyberpunk 2077": "RPG", "ELDEN RING": "RPG",
    "Stardew Valley": "시뮬레이션", "Dota 2": "AOS", "Rust": "생존"
}

def get_steam_data(steam_id):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {"key": STEAM_API_KEY, "steamid": steam_id, "format": "json", "include_appinfo": "1"}
    resp = requests.get(url, params=params)
    if resp.status_code != 200: return None
    data = resp.json()
    if not data.get('response') or 'games' not in data['response']: return None
    
    df = pd.DataFrame(data['response']['games'])
    # 플레이타임 0시간인 게임 걸러내기
    df = df[df['playtime_forever'] > 0]
    
    # 여기서 df가 비어버릴 수 있으니 체크 후 반환
    if df.empty:
        return df 
        
    df['플레이타임(시간)'] = df['playtime_forever'] / 60
    df['장르'] = df['name'].apply(lambda x: GENRE_MAP.get(x, '기타 장르'))
    return df.sort_values(by='플레이타임(시간)', ascending=False).reset_index(drop=True)

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
        elif my_df.empty: # ✨ [핵심 방어막] 데이터가 텅 비었을 때 뻗지 않게 막아줌!
            st.warning("⚠️ 이 계정은 1분 이상 플레이한 게임 기록이 전혀 없습니다!")
        else:
            st.divider()
            st.subheader("📸 Instagram 공유용 요약 카드")
            my_total_hours = my_df['플레이타임(시간)'].sum()
            my_top_game = my_df.iloc[0]['name']
            top_genre = my_df.groupby('장르')['플레이타임(시간)'].sum().idxmax()
            
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("총 갈아넣은 시간", f"{my_total_hours:,.0f} 시간")
                c2.metric("인생 최고의 게임", my_top_game)
                c3.metric("나의 게이밍 성향", f"{top_genre} 마스터")
                st.caption("✨ 캡처해서 인스타 스토리에 올려보세요! #SteamDNA #인생전적")

            st.subheader("🧬 나의 게이밍 장르 DNA")
            genre_df = my_df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
            fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', 
                                  textfont=dict(size=14, color='white'), marker=dict(line=dict(color='#000000', width=1)))
            st.plotly_chart(fig_pie, use_container_width=True)

            if friend_id:
                st.divider()
                st.header("⚔️ 전적 맞다이: 나 vs 친구")
                friend_df = get_steam_data(friend_id)
                
                if friend_df is None:
                    st.warning("친구 계정이 비공개이거나 데이터를 불러올 수 없습니다.")
                elif friend_df.empty:
                    st.warning("친구 계정은 플레이한 게임 기록이 없습니다. (부전승!)")
                else:
                    friend_total = friend_df['플레이타임(시간)'].sum()
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        st.subheader("👑 내 전적")
                        st.metric("총 플레이타임", f"{my_total_hours:,.0f} 시간")
                        st.dataframe(my_df[['name', '플레이타임(시간)']].head(5), use_container_width=True)
                    with b2:
                        st.subheader("⚔️ 상대방 전적")
                        delta_val = friend_total - my_total_hours
                        st.metric("총 플레이타임", f"{friend_total:,.0f} 시간", delta=f"나와의 차이: {delta_val:,.0f}시간", delta_color="inverse")
                        st.dataframe(friend_df[['name', '플레이타임(시간)']].head(5), use_container_width=True)
            else:
                st.info("💡 팁: 친구의 SteamID를 입력하면 전적 비교 배틀이 가능합니다!")
                
            st.divider()
            st.subheader("📊 전체 라이브러리 (상위 15개)")
            fig_bar = px.bar(my_df.head(15).sort_values(by='플레이타임(시간)', ascending=True), 
                             x='플레이타임(시간)', y='name', orientation='h', color='플레이타임(시간)')
            fig_bar.update_yaxes(title_text="")
            st.plotly_chart(fig_bar, use_container_width=True)
