import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Steam DNA & Battle", page_icon="🔥", layout="wide")

STEAM_API_KEY = "ACFFB08C7B7E24EAC7ED03414035F9DC"
MINIMUM_WAGE_2026 = 10320 

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

# ✨ [NEW] 현실적인 시간대로 조정한 팩폭 함수들
def get_university_tier(hours):
    if hours >= 2000: return "서울대 경영학과 수석 입학 🦅"
    elif hours >= 1000: return "인서울 최상위권 대학 프리패스 🏫"
    elif hours >= 500: return "과탑 먹고 4년 전액 장학금 💰"
    elif hours >= 200: return "학점 4.5 만점 졸업 🎓"
    else: return "기말고사 전과목 A+ 💯"

def get_coding_tier(hours):
    if hours >= 1000: return "파이썬 마스터 & 빅테크 프론트엔드 합격 🚀"
    elif hours >= 500: return "나만의 웹 플랫폼 런칭 및 수익 창출 💸"
    elif hours >= 200: return "코딩 부트캠프 수석 수료 💻"
    else: return "파이썬 기초 완강 🐍"

def get_lifestyle_tier(money):
    if money >= 10000000: return "포르쉐 박스터 1년 유지비 완납 🏎️"
    elif money >= 5000000: return "유럽 4개국 한 달 살기 초호화 여행 ✈️"
    elif money >= 1000000: return "최고급 오마카세 5번 플렉스 🍣"
    else: return "치킨 수십 마리 공중분해 🍗"

def get_steam_profile_name(steam_id):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}
    try:
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            players = resp.json().get('response', {}).get('players', [])
            if players: return players[0].get('personaname', '알 수 없는 유저')
    except: pass
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
    new_data = pd.DataFrame({'SteamID': [str(steam_id)], '닉네임': [nickname], '총_플레이타임(시간)': [total_hours], '인생_게임': [top_game], '게이밍_성향': [top_genre]})
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, dtype={'SteamID': str})
        df = df[df['SteamID'] != str(steam_id)] 
        df = pd.concat([df, new_data], ignore_index=True)
    else: df = new_data
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
                top_genre = top_genre_hours.idxmax() if top_genre_hours.idxmax() != '기타 장르' or len(top_genre_hours) == 1 else top_genre_hours.drop('기타 장르').idxmax()

                save_to_db(my_id, my_nickname, my_total_hours, my_top_game, top_genre)

                st.divider()
                st.subheader(f"📸 {my_nickname}님의 Instagram 공유용 카드")
                with st.container(border=True):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("총 갈아넣은 시간", f"{int(my_total_hours):,} 시간")
                    c2.metric("인생 최고의 게임", my_top_game[:12] + ".." if len(my_top_game) > 12 else my_top_game)
                    c3.metric("나의 게이밍 성향", f"{top_genre} 마스터")

                # ✨ [NEW] 4분할 갓생 팩폭 매트릭스 추가
                st.subheader("💥 팩폭: 이 시간에 게임 안 하고 갓생을 살았다면?")
                with st.container(border=True):
                    f1, f2 = st.columns(2)
                    f3, f4 = st.columns(2)
                    lost_money = my_total_hours * MINIMUM_WAGE_2026
                    
                    # TIGER 미국 S&P500 등락을 고려해 대략 주당 18,000원으로 산정
                    etf_shares = int(lost_money / 18000) 
                    
                    f1.metric("💸 증발한 내 알바비 (시급 10,320원)", f"약 {int(lost_money / 10000):,}만 원", delta=f"TIGER 미국 S&P500 ETF 약 {etf_shares:,}주 매수 가능", delta_color="inverse")
                    f2.metric("🏎️ 잃어버린 라이프스타일", get_lifestyle_tier(lost_money), delta="통장 잔고 증발...", delta_color="inverse")
                    f3.metric("📚 잃어버린 학벌 및 성적", get_university_tier(my_total_hours), delta="내 잃어버린 학점...", delta_color="inverse")
                    f4.metric("💻 잃어버린 자기계발", get_coding_tier(my_total_hours), delta="개발자 취업 기회 증발...", delta_color="inverse")

                st.divider()
                st.subheader("🧬 나의 게이밍 장르 DNA")
                genre_df = my_df.groupby('장르')['플레이타임(시간)'].sum().reset_index().sort_values(by='플레이타임(시간)', ascending=False)
                if len(genre_df) > 5:
                    top_4 = genre_df.head(4)
                    others_hours = genre_df.iloc[4:]['플레이타임(시간)'].sum()
                    genre_df = pd.concat([top_4, pd.DataFrame({'장르': ['그 외 잡다한 장르들'], '플레이타임(시간)': [others_hours]})], ignore_index=True)
                genre_df['포맷_시간'] = genre_df['플레이타임(시간)'].apply(format_playtime)
                fig_pie = px.pie(genre_df, values='플레이타임(시간)', names='장르', hole=0.4)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(size=14, color='white'), customdata=genre_df['포맷_시간'], hovertemplate="<b>%{label}</b><br>플레이타임: %{customdata}<extra></extra>")
                st.plotly_chart(fig_pie, use_container_width=True)

                st.subheader(f"📊 {my_nickname}님의 전체 라이브러리 TOP 15")
                top15_df = my_df.head(15).sort_values(by='플레이타임(시간)', ascending=True)
                fig_bar = px.bar(top15_df, x='플레이타임(시간)', y='name', orientation='h', color='플레이타임(시간)')
                fig_bar.update_yaxes(title_text="")
                fig_bar.update_traces(text=top15_df['표기용_시간'], textposition='inside', insidetextanchor='middle', hovertemplate="<b>%{y}</b><br>플레이타임: %{text}<extra></extra>")
                st.plotly_chart(fig_bar, use_container_width=True)

                if friend_id:
                    st.divider()
                    st.header("🥊 라운드별 영혼의 맞다이: 나 vs 친구")
                    friend_df = get_steam_data(friend_id)
                    
                    if friend_df is not None and not friend_df.empty:
                        friend_nickname = get_steam_profile_name(friend_id)
                        friend_total = friend_df['플레이타임(시간)'].sum()
                        
                        f_top_genre_hours = friend_df.groupby('장르')['플레이타임(시간)'].sum()
                        f_top_genre = f_top_genre_hours.idxmax() if f_top_genre_hours.idxmax() != '기타 장르' or len(f_top_genre_hours) == 1 else f_top_genre_hours.drop('기타 장르').idxmax()
                        save_to_db(friend_id, friend_nickname, friend_total, friend_df.iloc[0]['name'], f_top_genre)
                        
                        st.subheader(f"Round 1. 총 잉여 시간 대결 (승자: {'나 👑' if my_total_hours > friend_total else '친구 👑'})")
                        b1, b2 = st.columns(2)
                        b1.metric(f"나 ({my_nickname})", f"{int(my_total_hours):,} 시간")
                        b2.metric(f"친구 ({friend_nickname})", f"{int(friend_total):,} 시간", delta=f"{int(friend_total - my_total_hours)}시간 차이", delta_color="inverse")

                        st.write("▼ 양측 상위 5개 게임 전적 비교")
                        t1, t2 = st.columns(2)
                        with t1:
                            st.dataframe(my_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'}), use_container_width=True, hide_index=True)
                        with t2:
                            st.dataframe(friend_df[['name', '표기용_시간']].head(5).rename(columns={'name':'게임명', '표기용_시간':'플레이타임'}), use_container_width=True, hide_index=True)

                        my_top_time = my_df.iloc[0]['플레이타임(시간)']
                        fr_top_time = friend_df.iloc[0]['플레이타임(시간)']
                        st.subheader(f"Round 2. 한 우물(1위 게임) 썩은물 대결 (승자: {'나 👑' if my_top_time > fr_top_time else '친구 👑'})")
                        r2_1, r2_2 = st.columns(2)
                        r2_1.metric(f"나의 최애: {my_top_game}", f"{int(my_top_time)} 시간")
                        r2_2.metric(f"친구의 최애: {friend_df.iloc[0]['name']}", f"{int(fr_top_time)} 시간")

                        st.subheader("Round 3. ⚔️ 자존심이 걸린 공통 게임 맞다이")
                        common_df = pd.merge(my_df[['name', '플레이타임(시간)']], friend_df[['name', '플레이타임(시간)']], on='name', suffixes=('_나', '_친구'))
                        
                        if not common_df.empty:
                            common_df['합계'] = common_df['플레이타임(시간)_나'] + common_df['플레이타임(시간)_친구']
                            top_common = common_df.sort_values(by='합계', ascending=False).head(5)
                            
                            fig_battle = go.Figure(data=[
                                go.Bar(name=my_nickname, x=top_common['name'], y=top_common['플레이타임(시간)_나'], marker_color='#1f77b4'),
                                go.Bar(name=friend_nickname, x=top_common['name'], y=top_common['플레이타임(시간)_친구'], marker_color='#d62728')
                            ])
                            fig_battle.update_layout(barmode='group', title="같은 게임, 다른 인생 (공통 보유 게임 플레이타임 비교)")
                            st.plotly_chart(fig_battle, use_container_width=True)
                        else:
                            st.info("같이 한 게임이 하나도 없습니다! 성향이 완전히 반대네요.")

with tab2:
    st.header("🏆 글로벌 랭킹 (명예의 전당)")
    file_path = 'steam_leaderboard.csv'
    
    if os.path.exists(file_path):
        lb_df = pd.read_csv(file_path, dtype={'SteamID': str})
        lb_df = lb_df.sort_values(by='총_플레이타임(시간)', ascending=False)
        lb_df = lb_df.reset_index(drop=True)
        
        lb_df['순위'] = [f"{i+1}위" for i in range(len(lb_df))]
        lb_df['총 플레이타임'] = lb_df['총_플레이타임(시간)'].apply(format_playtime)
        
        display_lb = lb_df[['순위', '닉네임', '총 플레이타임', '인생_게임', '게이밍_성향']].set_index('순위')
        st.dataframe(display_lb, use_container_width=True)
