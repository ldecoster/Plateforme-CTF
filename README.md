# ![](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/logo.png?raw=true)

## What is CTFd?

CTFd is a Capture The Flag framework focusing on ease of use and customizability. It comes with everything you need to run a CTF and it's easy to customize with plugins and themes.

## Features

- Create your own challenges, tags, resources, and flags from the Admin Interface
  - Unlockable challenge support
  - Challenge plugin architecture to create your own custom challenges
  - Static & Regex based flags
    - Custom flag plugins
  - File uploads to the server
  - Hide challenges
  - Automatic bruteforce protection
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
- Possibility to each user to add their school and cursus
- Generate a data visualization dashboard with Kibana
  - Most solved challenges
  - Number of total solved challenges
  - Number of register users
  - Distribution of users by schools and specialities
  - Ratio of correct and incorrect answers
- And a lot more...

## Install

### Install production server (Ubuntu 20.04 for instance)

1. Install Python 3.7
  - `sudo add-apt-repository ppa:deadsnakes/ppa`
  - `sudo apt-get update`
  - `sudo apt install python3.7 python3.7-venv`
2. Clone project and create a python virtual environment
  - `git clone https://github.com/ldecoster/Plateforme-CTF.git`
  - `cd Plateforme-CTF`
  - `python3.7 -m venv env`
3. Install pip dependencies through the virtual environment
  - `source env/bin/activate`
  - `pip install wheel gunicorn`
  - `pip install -r requirements.txt`
4. Run project with an IP address
  - `gunicorn --workers={WORKER_NUMBER} --bind {IP_ADDRESS}:8000 "CTFd:create_app()"` where {WORKER_NUMBER} is equal to (2 x the number of cores of the server) + 1 and {IP_ADDRESS} is the IP address of the server on the network

### Install ElasticSearch and Kibana

1. Download [ElasticSearch](https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.12.1-amd64.deb) and [Kibana](https://artifacts.elastic.co/downloads/kibana/kibana-7.12.1-amd64.deb) version 7.12.1
2. Install them
  - `sudo dpkg -i elasticsearch-7.12.1-amd64.deb`
  - `sudo dpkg -i kibana-7.12.1-amd64.deb`
3. Optional: Expose Kibana on a network instead of localhost (Security Warning: as there is no authentication, everyone on the network can see the data exposed by Kibana)
  - Edit `/etc/kibana/kibana.yml` file
  - Edit the line `#server.host: "localhost"` to `server.host: "{IP_ADDRESS}"` where {IP_ADDRESS} is the IP address of the server
4. Start them and enable launching on startup
  - `sudo systemctl enable --now elasticsearch.service`
  - `sudo systemctl enable --now kibana.service`
5. From Kibana interface [localhost:5601](http://localhost:5601)
  - Click on "Stack Management" menu
  - Select "Saved Object"
  - Click on the "import" button and select the file `admin_dashboard.ndjson` from the project. Keep the option "Check for existing objects" checked and validate
6. Run the export script in a new terminal
  - `source env/bin/activate`
  - `python export_es.py`
7. Back to Kibana interface [localhost:5601](http://localhost:5601)
  - Click on "Dashboard" menu
  - Select `Admin dashboard` to visualize all the graphs

### Legacy (debug) install of CTFd

1. Install dependencies: `pip install -r requirements.txt`
   1. You can also use the `prepare.sh` script to install system dependencies using apt.
2. Modify [CTFd/config.ini](https://github.com/CTFd/CTFd/blob/master/CTFd/config.ini) to your liking.
3. Use `python serve.py` or `flask run` in a terminal to drop into debug mode.
4. Use `yarn` or `npm` to rebuild static files (JS, CSS, etc.)

You can use the auto-generated Docker images with the following command:

`docker run -p 8000:8000 -it ctfd/ctfd`

Or you can use Docker Compose with the following command from the source repository:

`docker-compose up`

Check out the [CTFd docs](https://docs.ctfd.io/) for [deployment options](https://docs.ctfd.io/docs/deployment/) and the [Getting Started](https://docs.ctfd.io/tutorials/getting-started/) guide

## Credits

### Original CTFd
- Original CTFd by [Kevin Chung](https://ctfd.io)
- Logo by [Laura Barbera](http://www.laurabb.com/)
- Theme by [Christopher Thompson](https://github.com/breadchris)
- Notification Sound by [Terrence Martin](https://soundcloud.com/tj-martin-composer)

### Customized CTFd
- Solène CORRE
- Loïc DECOSTER
- Lina KADA
- Sébastien LEGAIT
- Julien LECOEUCHE
- Maxime MARE
- Kylian SALOMON
- Maxime THOOR
