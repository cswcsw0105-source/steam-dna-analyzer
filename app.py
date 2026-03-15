import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Steam DNA & Battle", page_icon="🔥", layout="wide")

STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"

GENRE_MAP = {
    "Tom Clancy's Rainbow Six Siege": "FPS", "PUBG: BATTLEGROUNDS": "FPS", 
    "Apex Legends": "FPS", "Counter-Strike 2": "FPS", "Overwatch 2": "FPS",
    "Grand Theft Auto V": "오픈월드", "Grand Theft Auto V Legacy": "오픈월드", 
    "Cyberpunk 2077": "RPG", "ELDEN RING": "RPG",
    "Stardew Valley": "시뮬레이션", "Dota 2": "AOS", "Rust": "생존",
    "TEKKEN 7": "격투", "F1® 24": "레이싱" 
}

def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if h == 0: return f"{m}분"
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

# ✨ [NEW] 스팀 프로필 '닉네임'을 자동으로 훔쳐(?)오는 함수
def get_steam_profile_name(steam_id):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}
    try:
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            players = resp.json().get('response', {}).get('players', [])
            if players:
                return players[0].get('personaname', '알 수 없는 유저')
    except:
        pass
    return "알 수 없는 유저"

def get_steam_data(steam_id):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {"key": STEAM_API_KEY, "steamid": steam_id, "format": "json", "include_appinfo": "1"}
    resp = requests.get(url, params=params)
    if resp.status_code != 200: return None
    data = resp.json()
    if not data.get('response') or 'games' not in data['response']: return None
    
    df = pd.DataFrame(data['response']['games'])
    df = df[df['playtime_forever'] > 0]
    
    if df.empty: return df 
        
    df['플레이타임(시간)'] = df['playtime_forever'] / 60
    df['표기용_시간'] = df['플레이타임(시간)'].apply(format_playtime)
    df['장르'] = df['name'].apply(lambda x: GENRE_MAP.get(x, '기타 장르'))
    return df.sort_values(by='플레이타임(시간)', ascending=False).reset_index(drop=True)

# ✨ [FIX] 중복 저장 완벽 차단 및 닉네임 저장 추가
def save_to_db(steam_id, nickname, total_hours, top_game, top_genre):
    file_path = 'steam_leaderboard.csv'
    new_data = pd.DataFrame({
        'SteamID': [str(steam_id)],  # 무조건 텍스트로 고정
        '닉네임': [nickname],        # 스팀 닉네임 추가!
        '총_플레이타임(시간)': [total_hours],
        '인생_게임': [top_game],
        '게이밍_성향': [top_genre]
    })
    
    if os.path.exists(file_path):
        # 읽어올 때도 SteamID를 무조건 텍스트(str)로 읽게 강제 지정
        df = pd.read_csv(file_path, dtype={'SteamID': str})
        # 기존에 있던 내 기록 삭제 (중복 방지)
        df = df[df['SteamID'] != str(steam_id)] 
        # 최신 기록으로 밑에 이어 붙이기
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
        
    df.to_csv(file_path, index=False)

st.title("🔥 스팀 게이밍 DNA & 전적 배틀")

tab1, tab2 = st.tabs(["🎮 전적 분석 & 배틀", "🏆 명예의 전당 (리더보드)"])

with tab1:
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        my_id = st.text_input("👑 내 SteamID64 (필수):", "76561198028121353")
    with col_search2:
        friend_id = st.text_input("⚔️ 친구 SteamID64 (배틀용, 선택):", "")

    if st.button("전적 분석 & 배틀 시작!"):
        with st.spinner('서버에서 데이터를 불러오는 중...'):
            my_df = get_steam_data(my_id)
            
            if my_df is None:
                st.error("내 계정 데이터를 불러올 수 없습니다.")
            elif my_df.empty:
                st.warning("⚠️ 이 계정은 1분 이상 플레이한 게임 기록이 전혀 없습니다!")
            else:
                my_nickname = get_steam_profile_name(my_id) # 닉네임 훔쳐오기
                my_total_hours = my_df['플레이타임(시간)'].sum()
                my_top_game = my_df.iloc[0]['name']
                
                top_genre_hours = my_df.groupby('장르')['플레이타임(시간)'].sum()
                top_genre = top_genre_hours.idxmax()
                if top_genre == '기타 장르' and len(top_genre_hours) > 1:
                    top_genre = top_genre_hours.drop('기타 장르').idxmax()

                save_to_db(my_id, my_nickname, my_total_hours, my_top_game, top_genre)

                st.divider()
                st.subheader(f"📸 {my_nickname}님의 Instagram 공유용 카드")
                with st.container(border=True):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("총 갈아넣은 시간", f"{int(my_total_hours):,} 시간")
                    c2.metric("인생 최고의 게임", my_top_game[:15] + ".." if len(my_top_game) > 15 else my_top_game)
                    c3.metric("나의 게이밍 성향", f"{top_genre} 마스터")
                    st.caption("✨ 캡처해서 인스타 스토리에 올려보세요! #SteamDNA #인생전적")

                st.subheader("🧬 나의 게이밍 장르 DNA")
                genre_df = my_df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
                genre_df['포맷_시간'] = genre_df['플레이타임(시간)'].apply(format_playtime)
                fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4)
                fig_pie.update_traces(
                    textposition='inside', textinfo='percent+label', 
                    textfont=dict(size=14, color='white'), marker=dict(line=dict(color='#000000', width=1)),
                    customdata=genre_df['포맷_시간'], hovertemplate="<b>%{label}</b><br>플레이타임: %{customdata}<extra></extra>"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

                if friend_id:
                    st.divider()
                    st.header("⚔️ 전적 맞다이: 나 vs 친구")
                    friend_df = get_steam_data(friend_id)
                    
                    if friend_df is not None and not friend_df.empty:
                        friend_nickname = get_steam_profile_name(friend_id)
                        friend_total = friend_df['플레이타임(시간)'].sum()
                        
                        friend_top_game = friend_df.iloc[0]['name']
                        friend_genre_hours = friend_df.groupby('장르')['플레이타임(시간)'].sum()
                        f_top_genre = friend_genre_hours.idxmax()
                        if f_top_genre == '기타 장르' and len(friend_genre_hours) > 1:
                            f_top_genre = friend_genre_hours.drop('기타 장르').idxmax()
                        save_to_db(friend_id, friend_nickname, friend_total, friend_top_game, f_top_genre)
                        
                        b1, b2 = st.columns(2)
                        with b1:
                            st.subheader(f"👑 {my_nickname} 전적")
                            st.metric("총 플레이타임", f"{int(my_total_hours):,} 시간")
                            st.dataframe(my_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'}), use_container_width=True, hide_index=True)
                        with b2:
                            st.subheader(f"⚔️ {friend_nickname} 전적")
                            delta_val = friend_total - my_total_hours
                            st.metric("총 플레이타임", f"{int(friend_total):,} 시간", delta=f"나와의 차이: {int(delta_val):,}시간", delta_color="inverse")
                            st.dataframe(friend_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'}), use_container_width=True, hide_index=True)
                    
                st.divider()
                st.subheader("📊 전체 라이브러리 (상위 15개)")
                top15_df = my_df.head(15).sort_values(by='플레이타임(시간)', ascending=True)
                fig_bar = px.bar(top15_df, x='플레이타임(시간)', y='name', orientation='h', color='플레이타임(시간)')
                fig_bar.update_yaxes(title_text="")
                fig_bar.update_traces(text=top15_df['표기용_시간'], textposition='inside', insidetextanchor='middle', hovertemplate="<b>%{y}</b><br>플레이타임: %{text}<extra></extra>")
                st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.header("🏆 글로벌 랭킹 (명예의 전당)")
    st.write("우리 플랫폼에서 전적을 분석한 유저들의 플레이타임 랭킹입니다.")
    
    file_path = 'steam_leaderboard.csv'
    if os.path.exists(file_path):
        lb_df = pd.read_csv(file_path, dtype={'SteamID': str})
        lb_df = lb_df.sort_values(by='총_플레이타임(시간)', ascending=False).reset_index(drop=True)
        lb_df['순위'] = [f"{i+1}위" for i in range(len(lb_df))]
        
        lb_df['총 플레이타임'] = lb_df['총_플레이타임(시간)'].apply(format_playtime)
        # ✨ 17자리 숫자 빼고 '닉네임'으로 깔끔하게 출력
        display_lb = lb_df[['순위', '닉네임', '총 플레이타임', '인생_게임', '게이밍_성향']].set_index('순위')
        
        st.dataframe(display_lb, use_container_width=True)
    else:
        st.info("아직 등록된 게이머가 없습니다. 첫 번째로 전적을 분석하고 1위를 차지하세요!")
