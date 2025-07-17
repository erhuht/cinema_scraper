from bs4 import BeautifulSoup


def populate_html(movies):
    with open('template.html', encoding="utf-8") as template:
        soup = BeautifulSoup(template.read(), "html.parser")

    movie_template = soup.find('div', attrs={'class': 'movie'})
    html_start = str(soup)[:str(soup).find(str(movie_template))]
    html_end = str(soup)[str(soup).find(
        str(movie_template))+len(str(movie_template)):]

    movie_entries = []
    for movie in movies:
        movie_template.find("p", class_="title").string.replace_with(
            movie["og_title"])

        # Remove the br elements from the previous iteration
        for t in movie_template.a.findChildren():
            t.extract()
        movie_template.a.smooth()

        for t in movie_template.find("p", class_="dates").findChildren():
            t.extract()
        movie_template.find("p", class_="dates").smooth()

        movie_template.find("em").string.replace_with(
            movie["letterboxd_info"]["director"])

        # Weird, because of different formats
        dates = ", ".join(movie["date"]).split(", ")
        movie_template.find("p", class_="dates").string.replace_with(
            dates[0].title())
        for date in dates[1:]:
            movie_template.find("p", class_="dates").append(soup.new_tag("br"))
            movie_template.find("p", class_="dates").append(
                soup.new_string(date.title()))

        if type(movie["theater"]) == list:
            theater_name = movie["theater"][0]
            movie_template.a.string.replace_with(theater_name)
            for theater in movie["theater"][1:]:
                movie_template.a.append(soup.new_tag("br"))
                movie_template.a.append(soup.new_string(theater))
        else:
            theater_name = movie["theater"]
            movie_template.a.string.replace_with(theater_name)

        movie_template.a["href"] = movie["info"]["human_url"]

        movie_template.img["src"] = movie["letterboxd_info"]["poster"]
        movie_template.img["alt"] = movie["title"]
        movie_entries.append(str(movie_template))

    return html_start + "\n".join(movie_entries) + html_end
