from bs4 import BeautifulSoup
from pathlib import Path
import re
from datetime import datetime
import copy
from mjml import mjml_to_html


def populate_html(movies):
    with open(Path(__file__).parent / 'template.mjml', encoding="utf-8") as template:
        soup = BeautifulSoup(template.read(), "html.parser")

    subtitle_section = soup.find(
        'mj-section', attrs={'css-class': 'subtitle-section'})
    movie_section = soup.find(
        'mj-section', attrs={'css-class': 'movie-section'})
    movie_template = soup.find('mj-column', attrs={'css-class': 'movie'})
    mjml_start = str(soup)[:str(soup).find(str(subtitle_section))]
    mjml_end = str(soup)[str(soup).find(
        str(movie_section))+len(str(movie_section)):]

    title = datetime.now().strftime("Helsingin elokuvauutiskirje %m/%y")
    mjml_start = mjml_start.replace("TITLE", title)

    section_dict = {"Watchlist": [], "Tykätyt": []}

    for movie in movies:
        if section_dict.get(movie["letterboxd_info"]["section"]):
            section_dict[movie["letterboxd_info"]["section"]].append(movie)
        else:
            section_dict[movie["letterboxd_info"]["section"]] = [movie]

    # Make sure watchlist goes first
    sections = [{"name": "Watchlist", "movies": section_dict.pop(
        "Watchlist")}, {"name": "Tykätyt", "movies": section_dict.pop("Tykätyt")}]
    sections += [{"name": key, "movies": value}
                 for key, value in section_dict.items()]

    section_entries = []
    for section in sections:
        movie_section_copy = copy.copy(movie_section)
        movie_entries = []
        for movie in section["movies"]:
            movie_copy = copy.copy(movie_template)
            movie_copy.find("h2").string.replace_with(
                movie["og_title"])
            movie_copy.find("em").string.replace_with(
                movie["letterboxd_info"]["director"])

            dates = movie["date"]
            movie_copy.find("p", attrs={"css-class": "dates"}).string.replace_with(
                dates[0].title())
            for date in dates[1:]:
                movie_copy.find(
                    "p", attrs={"css-class": "dates"}).append(soup.new_tag("br"))
                movie_copy.find("p", attrs={"css-class": "dates"}).append(
                    soup.new_string(date.title()))

            if type(movie["theater"]) == list:
                theater_name = movie["theater"][0]
                movie_copy.a.string.replace_with(theater_name)
                for theater in movie["theater"][1:]:
                    movie_copy.a.append(soup.new_tag("br"))
                    movie_copy.a.append(soup.new_string(theater))
            else:
                theater_name = movie["theater"]
                movie_copy.a.string.replace_with(theater_name)

            movie_copy.a["href"] = movie["info"]["human_url"]
            movie_copy.find("a", string=re.compile("Letterboxd"))[
                "href"] = movie["letterboxd_info"]["url"]

            movie_copy.img["src"] = movie["letterboxd_info"]["poster"]
            movie_copy.img["alt"] = movie["title"]
            movie_entries.append(movie_copy)
        movie_section_copy.find("mj-column", attrs={"css-class": "movie"}).replace_with(
            *movie_entries)
        section_entries.append(str(subtitle_section).replace("SUBTITLE", section["name"]) +
                               "\n" + str(movie_section_copy))

    mjml_output = mjml_start + "\n".join(section_entries) + mjml_end
    html_output = mjml_to_html(mjml_output).html
    return title, html_output
