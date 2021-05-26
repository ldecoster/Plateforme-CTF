# ![](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/logo.png?raw=true)

![CTFd MySQL CI](https://github.com/CTFd/CTFd/workflows/CTFd%20MySQL%20CI/badge.svg?branch=master)
![Linting](https://github.com/CTFd/CTFd/workflows/Linting/badge.svg?branch=master)
[![MajorLeagueCyber Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fcommunity.majorleaguecyber.org%2F)](https://community.majorleaguecyber.org/)
[![Documentation Status](https://api.netlify.com/api/v1/badges/6d10883a-77bb-45c1-a003-22ce1284190e/deploy-status)](https://docs.ctfd.io)

## What is CTFd?

CTFd is a Capture The Flag framework focusing on ease of use and customizability. It comes with everything you need to run a CTF and it's easy to customize with plugins and themes.

![CTFd is a CTF in a can.](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/scoreboard.png?raw=true)

## Features

- Create your own challenges, categories, hints, and flags from the Admin Interface
  - Unlockable challenge support
  - Challenge plugin architecture to create your own custom challenges
  - Static & Regex based flags
    - Custom flag plugins
  - Unlockable hints
  - File uploads to the server
  - Hide challenges
  - Automatic bruteforce protection
- Scoreboard with automatic tie resolution
- Add tag on challenge
- Create Exercise by grouping multiple challenges
- Create badge & assign it to players
  - Link a badge to an exercise
- Markdown content management system
- Team management, hiding, and banning
- Customize everything using the [plugin](https://docs.ctfd.io/docs/plugins/) and [theme](https://docs.ctfd.io/docs/themes/) interfaces
- Importing and Exporting of CTF data for archival
- Various sort for challenges
- Create profile with customs rights & access
  - Administrator
  - Teacher
  - Contributor
  - User
- Voting system to have a challenge checked by contributors
  - Possibility to change the minimum number of votes required
- Possibility to each users to add their school and cursus
- Generate a data visualization dashboard with elasticShearch
  - Most solved challenges
  - Number of total solved challenges
  - Number of register users
  - Distribution of users by schools and specialities
  - Ratio of correct and incorrect answers
- And a lot more...

## Install

1. Install python3 & pip dependancies
   - `sudo apt install python3-pip`
   - `pip install wheel`
   - `pip install waitress`
   - `pip install Flask`
   - `apt-get install python3-waitress`
   - `apt-get install python3-venv`
2. Install dependencies: `pip install -r requirements.txt`
   1. You can also use the `prepare.sh` script to install system dependencies using apt.
3. Modify [CTFd/config.ini](https://github.com/CTFd/CTFd/blob/master/CTFd/config.ini) to your liking.
4. Change `FLASK_ENV` variable in `.flaskenv` to `prod`
5. Create environment :
   1. `python3 -m venv venv`
   2. `. venv/bin/activate`
6. Use `python serve.py` or `flask run` in a terminal to drop into debug mode.

You can use the auto-generated Docker images with the following command:

`docker run -p 8000:8000 -it ctfd/ctfd`

Or you can use Docker Compose with the following command from the source repository:

`docker-compose up`

Check out the [CTFd docs](https://docs.ctfd.io/) for [deployment options](https://docs.ctfd.io/docs/deployment/) and the [Getting Started](https://docs.ctfd.io/tutorials/getting-started/) guide

server creds :

`Identifiant :isen`

`password: isen62`



## Credits

- Logo by [Laura Barbera](http://www.laurabb.com/)
- Theme by [Christopher Thompson](https://github.com/breadchris)
- Notification Sound by [Terrence Martin](https://soundcloud.com/tj-martin-composer)
