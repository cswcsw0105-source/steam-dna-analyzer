import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam DNA & Battle", page_icon="🔥", layout="wide")

STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"

# 선웅이 맞춤형으로 캡처본에 있던 게임들 장르 추가!
GENRE_MAP = {
    "Tom Clancy's Rainbow Six Siege": "FPS", "PUBG: BATTLEGROUNDS": "FPS", 
    "Apex Legends": "FPS", "Counter-Strike 2": "FPS", "Overwatch 2": "FPS",
    "Grand Theft Auto V": "오픈월드", "Grand Theft Auto V Legacy": "오픈월드", # 레거시 버전 추가
    "Cyberpunk 2077": "RPG", "ELDEN RING": "RPG",
    "Stardew Valley": "시뮬레이션", "Dota 2": "AOS", "Rust": "생존",
    "TEKKEN 7": "격투", "F1® 24": "레이싱" # 선웅이 픽 추가
}

# 잃어버렸던 시간 변환 함수 부활!
def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if h == 0: return f"{m}분"
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

def get_steam_data(steam_id):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {"key": STEAM_API_KEY, "steamid": steam_id, "format": "json", "include_appinfo": "1"}
    resp = requests.get(url, params=params)
    if resp.status_code != 200: return None
    data = resp.json()
    if not data.get('response') or 'games' not in data['response']: return None
    
    df = pd.DataFrame(data['response']['games'])
    df = df[df['playtime_forever'] > 0]
    
    if df.empty:
        return df 
        
    df['플레이타임(시간)'] = df['playtime_forever'] / 60
    # 표기용 깔끔한 시간 컬럼 추가
    df['표기용_시간'] = df['플레이타임(시간)'].apply(format_playtime)
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
        elif my_df.empty:
            st.warning("⚠️ 이 계정은 1분 이상 플레이한 게임 기록이 전혀 없습니다!")
        else:
            st.divider()
            st.subheader("📸 Instagram 공유용 요약 카드")
            my_total_hours = my_df['플레이타임(시간)'].sum()
            my_top_game = my_df.iloc[0]['name']
            
            # 장르가 '기타 장르'만 있으면 뻘쭘하니까 제일 많이 한 게임 이름을 띄우게 수정
            top_genre_hours = my_df.groupby('장르')['플레이타임(시간)'].sum()
            top_genre = top_genre_hours.idxmax()
            if top_genre == '기타 장르' and len(top_genre_hours) > 1:
                top_genre = top_genre_hours.drop('기타 장르').idxmax()

            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("총 갈아넣은 시간", f"{int(my_total_hours):,} 시간")
                c2.metric("인생 최고의 게임", my_top_game[:15] + ".." if len(my_top_game) > 15 else my_top_game)
                c3.metric("나의 게이밍 성향", f"{top_genre} 마스터")
                st.caption("✨ 캡처해서 인스타 스토리에 올려보세요! #SteamDNA #인생전적")

            st.subheader("🧬 나의 게이밍 장르 DNA")
            genre_df = my_df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
            # 파이 차트 툴팁용 시간 포맷팅
            genre_df['포맷_시간'] = genre_df['플레이타임(시간)'].apply(format_playtime)
            
            fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4)
            # 마우스 올렸을 때 소수점 안 나오게 포맷팅된 시간 적용
            fig_pie.update_traces(
                textposition='inside', textinfo='percent+label', 
                textfont=dict(size=14, color='white'), 
                marker=dict(line=dict(color='#000000', width=1)),
                customdata=genre_df['포맷_시간'],
                hovertemplate="<b>%{label}</b><br>플레이타임: %{customdata}<extra></extra>"
            )
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
                        st.metric("총 플레이타임", f"{int(my_total_hours):,} 시간")
                        # 소수점 다 빼고 깔끔한 컬럼만 출력
                        display_my = my_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'})
                        st.dataframe(display_my, use_container_width=True, hide_index=True)
                    with b2:
                        st.subheader("⚔️ 상대방 전적")
                        delta_val = friend_total - my_total_hours
                        st.metric("총 플레이타임", f"{int(friend_total):,} 시간", delta=f"나와의 차이: {int(delta_val):,}시간", delta_color="inverse")
                        display_friend = friend_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'})
                        st.dataframe(display_friend, use_container_width=True, hide_index=True)
            else:
                st.info("💡 팁: 친구의 SteamID를 입력하면 전적 비교 배틀이 가능합니다!")
                
            st.divider()
            st.subheader("📊 전체 라이브러리 (상위 15개)")
            top15_df = my_df.head(15).sort_values(by='플레이타임(시간)', ascending=True)
            fig_bar = px.bar(top15_df, x='플레이타임(시간)', y='name', orientation='h', color='플레이타임(시간)')
            fig_bar.update_yaxes(title_text="")
            # 막대그래프 안에도 깔끔하게 '시간 분' 박아주기
            fig_bar.update_traces(
                text=top15_df['표기용_시간'], 
                textposition='inside', 
                insidetextanchor='middle',
                hovertemplate="<b>%{y}</b><br>플레이타임: %{text}<extra></extra>"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
