"""
    ADIPOSE Sequence Controller
    URY AutoPlayout and Sequencing Controller
    @author Michael Grace, October 2020
"""

import config
import requests
import time
from flask import Flask, request

app = Flask(__name__)
start_time = time.time()

sequencedShow = False
currentTimeslotID = None
currentSequence = []
currentItemID = None
tracklistItem = None

def api_response(payload, ok = True):
    return {
        "status": "OK" if ok else "FAIL",
        "payload": payload
    }

def my_radio_api_request(endpoint, http = "GET", params = False, data = None):
    myradio = config.DEV_URL if config.DEV_MODE else config.BASE_URL
    key_sym = "?" if not params else "&"
    http = http.upper()

    if http == "GET":
        return requests.get(myradio + endpoint + key_sym + "api_key=" + config.API_KEY).json()
    elif http == "POST":
        return requests.post(myradio + endpoint + key_sym + "api_key=" + config.API_KEY, data=data).json()
    elif http == "PUT":
        return requests.put(myradio + endpoint + key_sym + "api_key=" + config.API_KEY, data=data).json()

@app.route("/request")
def get():
    if request.remote_addr != config.REQUEST_ALLOW:
        print("Unauthorised Request", flush=True)
        return api_response("Caller can't access this endpoint.", False), 403

    global sequencedShow
    global currentTimeslotID
    global currentSequence
    global currentItemID
    global tracklistItem

    print("Getting Audio Request", flush=True)

    # Finish Previous Tracklist
    if tracklistItem and config.TRACKLISTING:
        print("Finishing Tracklist: {}".format(tracklistItem), flush=True)
        my_radio_api_request("tracklistItem/{}/endtime".format(tracklistItem), "PUT")
        tracklistItem = None

    if sequencedShow:
        print("Getting Audio for Sequenced Show: {}".format(currentTimeslotID), flush=True)
        r = my_radio_api_request("timeslot/{}/showplan".format(currentTimeslotID))
        show_plan = r["payload"] # Needs Error Handling
        if type(show_plan) is dict:
            sequence = show_plan["0"]
        else:
            sequence = show_plan[0]

        foundNext = False

        # Do we have a sequence yet?
        if not currentItemID:
            print("Making Original Sequence", flush=True)
            currentSequence = sequence
            if len(currentSequence)>0:
                currentItemID = currentSequence[0]["timeslotitemid"]
                foundNext = True

        else:
            # Loop through current sequence to find jump in point
            for t in range(len(currentSequence)):
                currentItemID = currentSequence[t]["timeslotitemid"]
                for i in range(len(sequence)):
                    if sequence[i]["timeslotitemid"] == currentItemID:
                        # Jump In From Here
                        currentSequence = sequence[i+1:]
                        foundNext = True
                        break
                if foundNext:
                    break

        if foundNext and len(currentSequence) > 0:
            nextToPlay = currentSequence[0]
            if nextToPlay["type"] == "central":
                if config.TRACKLISTING:
                     tracklistItem = my_radio_api_request("tracklistItem", "POST", None, {"trackid": nextToPlay["trackid"], "sourceid": "s"})["payload"]["audiologid"]
                return api_response(nextToPlay)
            else:
                #Managed Items
                managedPath = my_radio_api_request("nipswebItem/{}/path".format(nextToPlay["managedid"]))["payload"]
                return api_response({
                    "path":   managedPath,
                    "trackid": 0,
		    "album": {
                        "recordid": 0
                    }
                })
        else:
            # The shows basically over (whether intentionally or not)
            sequencedShow = False
            currentTimeslotID = None
            currentSequence = []
            currentItemID = None
    
            return my_radio_api_request("iTones/trackforjukebox")

    else:
        return my_radio_api_request("iTones/trackforjukebox")

@app.route("/newSequence")
# Called each hour at 2 mins past to trigger a new sequence
def hourUpdate():
    global sequencedShow
    global currentTimeslotID
    global currentSequence

    if request.remote_addr != config.TRIGGER_ALLOW:
        return api_response("Caller can't access this endpoint.", False), 403
    
    # Is show to be sequenced?
    current_timeslot = my_radio_api_request("timeslot/currentandnext?n=0", params=True)["payload"]["current"]
    if "id" in current_timeslot.keys(): # It's not jukebox
        playout_data = my_radio_api_request("timeslot/{}/playout".format(current_timeslot["id"]))["payload"]
        if playout_data: # This show is due to be played out :)
            sequencedShow = True
            currentTimeslotID = current_timeslot["id"]
            currentSequence = []

            # Jukebox Skip
            my_radio_api_request("iTones/skip")

            # Update Webcams
                # Needs Webcam Source
            
            # Update Mixclouder
            my_radio_api_request("timeslot/{}/meta".format(currentTimeslotID), "PUT", data = {"string_key": "upload_state", "value": "Played Out"})
    return status()


""" Does jukebox get a life?
    If not (when in a sequenced show),
    it won't tracklist or play its own jingles
"""
@app.route("/status")
def status():
    return api_response({
        "sequencedShow": sequencedShow,
        "timeslotID": currentTimeslotID
    })

@app.route("/ok")
def heartbeat():
    uptime = time.time() - start_time
    return api_response("Controller Uptime: {0}d{1}h{2}m{3}s".format(int(uptime//86400), int((uptime%86400)//3600), int((uptime%3600)//60), round(uptime%60)))

app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
