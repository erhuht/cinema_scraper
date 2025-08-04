# Cinema scraper

This project scrapes movie screenings in Helsinki, compares them to Letterboxd lists and compiles them into an automatic monthly newsletter using Scrapy, MJML and Github Actions.

## Features

Screenings are crawled from BioRex, Kino Regina, and [Kinot.fi](https://kinot.fi), as well as the seasonal films available to stream on Yle Areena.

The Letterboxd user's watchlist and likes are crawled, and any number of additional lists can be specified with `CUSTOM_LISTS`.

The workflow is scheduled in `main.yml` to run automatically on the 1st of each month at 03:00 UTC.

## Setup

To get the newsletter yourself, fork the repository and add repository secrets under **Settings → Secrets and variables → Actions**.

| Secret            | Description                                                                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `RECIPIENT_EMAIL` |                                                                                                                                                 |
| `LETTERBOXD_USER` |                                                                                                                                                 |
| `SENDER_EMAIL`    | Gmail address                                                                                                                                   |
| `SENDER_PASSWORD` | Gmail app password                                                                                                                              |
| `OMDB_KEY`        | API key to [OMDb](https://www.omdbapi.com/)                                                                                                     |
| `CUSTOM_LISTS`    | E.g. `[{"name":"Official Top 250 Narrative Feature Films","url":"https://letterboxd.com/dave/list/official-top-250-narrative-feature-films/"}]` |

Finally, enable the workflow under **Actions**.
