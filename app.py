import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Steam DNA & Battle", page_icon="🔥", layout="wide")

STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"

# 친구를 위한 '스포츠' 장르 등 대폭 추가
GENRE_MAP = {
    "Tom Clancy's Rainbow Six Siege": "FPS", "PUBG: BATTLEGROUNDS": "FPS", 
    "Apex Legends": "FPS", "Counter-Strike 2": "FPS", "Overwatch 2": "FPS",
    "Grand Theft Auto V": "오픈월드", "Grand Theft Auto V Legacy": "오픈월드", 
    "Cyberpunk 2077": "RPG", "ELDEN RING": "RPG",
    "Stardew Valley": "시뮬레이션", "Dota 2": "AOS", "Rust": "생존",
    "TEKKEN 7": "격투", "F1® 24": "레이싱", 
    "EA SPORTS FC™ 24": "스포츠", "FIFA 22": "스포츠", "FIFA 23": "스포츠", "Football Manager 2024": "스포츠"
}

def format_playtime(hours_float):
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    if h == 0: return f"{m}분"
    if m == 0: return f"{h}시간"
    return f"{h}시간 {m}분"

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

def save_to_db(steam_id, nickname, total_hours, top_game, top_genre):
    file_path = 'steam_leaderboard.csv'
    new_data = pd.DataFrame({
        'SteamID': [str(steam_id)],  
        '닉네임': [nickname],        
        '총_플레이타임(시간)': [total_hours],
        '인생_게임': [top_game],
        '게이밍_성향': [top_genre]
    })
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, dtype={'SteamID': str})
        df = df[df['SteamID'] != str(steam_id)] 
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
            
            if my_df is None or my_df.empty:
                st.error("데이터를 불러올 수 없거나 게임 기록이 없습니다.")
            else:
                my_nickname = get_steam_profile_name(my_id) 
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
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("총 갈아넣은 시간", f"{int(my_total_hours):,} 시간")
                    c2.metric("인생 최고의 게임", my_top_game[:12] + ".." if len(my_top_game) > 12 else my_top_game)
                    c3.metric("나의 게이밍 성향", f"{top_genre} 마스터")
                    
                    # ✨ [NEW] 마케팅 소구점: 시급 11,000원으로 환산한 기회비용 팩폭!
                    lost_money = my_total_hours * 11000
                    c4.metric("💸 이 시간에 알바를 했다면?", f"약 {int(lost_money / 10000):,}만 원", delta="증발해버린 내 돈...", delta_color="inverse")
                    
                    st.caption("✨ 캡처해서 친구를 도발해보세요! #SteamDNA #내돈내산시간")

                st.subheader("🧬 나의 게이밍 장르 DNA")
                # ✨ [NEW] 선웅이의 아이디어: 상위 4개 장르만 살리고 나머지는 기타로 묶기
                genre_df = my_df.groupby('장르')['플레이타임(시간)'].sum().reset_index()
                genre_df = genre_df.sort_values(by='플레이타임(시간)', ascending=False)
                
                if len(genre_df) > 5:
                    top_4 = genre_df.head(4)
                    others_hours = genre_df.iloc[4:]['플레이타임(시간)'].sum()
                    others_df = pd.DataFrame({'장르': ['그 외 잡다한 장르들'], '플레이타임(시간)': [others_hours]})
                    genre_df = pd.concat([top_4, others_df], ignore_index=True)
                
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
                            st.subheader(f"👑 {my_nickname}")
                            st.metric("총 플레이타임", f"{int(my_total_hours):,} 시간")
                            st.dataframe(my_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'}), use_container_width=True, hide_index=True)
                        with b2:
                            st.subheader(f"⚔️ {friend_nickname}")
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
    
    file_path = 'steam_leaderboard.csv'
    if os.path.exists(file_path):
        lb_df = pd.read_csv(file_path, dtype={'SteamID': str})
        lb_df = lb_df.sort_values(by='총_플레이타임(시간)', ascending=False).reset_index(drop=True)
        lb_df['순위'] = [f"{i+1}위" for i in range(len(lb_df))]
        
        lb_df['총 플레이타임'] = lb_df['총_플레이타임(시간)'].apply(format_playtime)
        display_lb = lb_df[['순위', '닉네임', '총 플레이타임', '인생_게임', '게이밍_성향']].set_index('순위')
        
        st.dataframe(display_lb, use_container_width=True)
