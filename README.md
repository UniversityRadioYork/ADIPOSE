# ADIPOSE - URY Sequence Controller

## Audio Dependent Independent Playout Option for Selected Ears

###### Originally Written by Michael Grace, October 2020

The sequence controller is the first version of the long awaited automatic playout of shows. It acts as a stage between jukebox and the MyRadio API, which will allow jukebox to ask MyRadio what to play most of the time, but if sequence controller knows it has a show to play, will tell jukebox to play that instead.

## Deployment

Sequence Controller is a Python Flask app, and the project can be run in Docker. Set your settings in `config.py`. If you want to specify a port other than 3000, that must also be changed in the Dockerfile.

### API Key

You'll need to have a MyRadio API Key for the project with the following permissions:

* `AUTH_JUKEBOX_MODIFYPLAYLISTS`
* `AUTH_EDITSHOWS`
* `AUTH_MODIFYWEBCAM`
* `AUTH_TRACKLIST_ALL`

### Docker

**Building Docker Image**

`docker build -t sequencer .`

**Running Docker**

`docker run -p PORT:PORT -d sequencer`

where `PORT` is the port the app runs on, specified in `config.py` and the Dockerfile.

### Jukebox

Jukebox can ask `myradio_sched.php` for what to play. The PHP can deal with the path differences between a track and a managed item (jingles etc.)

### Cronjob

Ensure a cronjob is running to `curl` the `/newSequence` endpoint at XX:02 each hour

## Endpoints

* `/request` (only accesable from address defined in `config.py`): This returns what the playout should play next, whether that be the response from MyRadio, a track from a show plan, or the key information about a managed item from the show plan.

* `/newSequence` (only accesable from address defined in `config.py`): allows the controller to check if the show is to be played out, and sets variables accordingly, and creates the original sequence

* `/status` returns information from the server, such as if something is being played out (sequencedShow). this'll allow jukebox to know whether it should play its own jingles and whether to tracklist by itself

* `/ok` "HELLO - ARE YOU OKAY?". Basically.
