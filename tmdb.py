from requests import Session
import os

TMDB_TOKEN = os.getenv("tmdb_token")

s = Session()
headers = {"accept": "application/json", "Authorization": f"Bearer {TMDB_TOKEN}"}
s.headers.update(headers)


def get_movie_info(movie_id="710295-wolf-man"):
    res = s.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_TOKEN}&language=zh-CN"
    )
    response = res.json()
    genres = response.get("genres")
    title = response.get("title")
    original_title = response.get("original_title")
    overview = response.get("overview")
    poster_path = response.get("poster_path")
    release_date = response.get("release_date")
    return {
        "title": title,
        "original_title": original_title,
        "release_date": release_date,
        "overview": overview,
        "genres": [g.get("name") for g in genres],
        "poster_path": f"https://image.tmdb.org/t/p/w600_and_h900_bestv2{poster_path}",
    }


def get_tv_info(tv_id="46260", season=1):
    # 火影忍者 46260
    # 安娜 196268
    res = s.get(
        f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_TOKEN}&language=zh-CN"
    )
    response = res.json()
    genres = response.get("genres")
    title = response.get("name")
    original_title = response.get("original_name")
    status = response.get("status")
    season_now = response.get("seasons")[season - 1]
    overview = season_now.get("overview")
    number_of_episodes_now = season_now.get("episode_count")
    poster_path = season_now.get("poster_path")
    release_date = season_now.get("air_date")
    season_name = season_now.get("name")
    return {
        "title": f"{title} - {season_name}",
        "original_title": original_title,
        "release_date": release_date,
        "status": status,
        "season": season,
        "number_of_episodes": number_of_episodes_now,
        "overview": overview,
        "genres": [g.get("name") for g in genres],
        "poster_path": f"https://image.tmdb.org/t/p/w600_and_h900_bestv2{poster_path}",
    }


if __name__ == "__main__":
    print(get_tv_info('1260951', 1))
    # print(get_movie_info())
