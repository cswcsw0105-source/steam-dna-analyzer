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

def get_university_tier(hours):
    if hours >= 10000: return "하버드·MIT 수석 입학 🎓"
    elif hours >= 5000: return "서울대 의대 프리패스 🩺"
    elif hours >= 3000: return "SKY (서연고) 프리패스 🦅"
    elif hours >= 1500: return "인서울 주요 대학 쌉가능 🏫"
    elif hours >= 500: return "지거국 수석 입학 🏛️"
    else: return "내신 1~2등급은 거뜬히 상승 📈"

def get_steam_profile_name(steam_id):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}
    try:
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            players = resp.json().get('response', {}).get('players', [])
            if players:
                return players[0].get('personaname', '알 수 없는 유저')
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
    col_search1, col
