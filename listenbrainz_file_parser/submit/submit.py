import pandas as pd
import json
import requests
import time
import sys


def submit_to_listenbrainz(payload, api_token, timeout):
    listenbrainz_submit = {
        "listen_type": "import",
        "payload": payload
    }
    listenbrainz_submit = json.dumps(listenbrainz_submit)
    print(api_token)
    print(type(api_token))
    r = requests.post("https://api.listenbrainz.org/1/submit-listens",
                      headers={'Authorization': 'Token ' + api_token}, data=listenbrainz_submit)
    print(r)
    print(r.json())
    if r.json()['status'] != 'ok':
        sys.exit()
    time.sleep(timeout)
    return 0


def make_payload(data_chunk, media_player):
    # yes, I know I shouldn't do iterrows, but I don't know what other option to do atm
    payload = []
    for row in data_chunk.iterrows():
        payload.append(make_listen(row[1], media_player))
    return payload


def make_listen(listen_series, media_player):
    listen_json = {
        "listened_at": listen_series['listened_at'],
        "track_metadata": {
            "artist_name": listen_series['artist_name'],
            "track_name": listen_series['track_name'],
            "release_name": listen_series['release_name'],
            "additional_info": {
                "media_player": media_player,
                "submission_client": "DataBase Listen Uploader by Coloradohusky",
            }
        }
    }
    for arg in listen_series.index:
        if (arg not in ['release_name', 'track_name', 'artist_name', 'listened_at']) and \
                (listen_series[arg] is True):
            listen_json['track_metadata']['additional_info'][arg] = listen_series[arg]
    return listen_json


def import_listens(file, media_player, api_token, max_batch, max_total, timeout):
    data = pd.read_excel(file, dtype="str")
    # how many listens to submit to ListenBrainz at once
    # add in some way to set --max-total
    if max_total == -1:
        max_total = len(data)
    for i in range(0, int(max_total / max_batch) + 1):
        data_chunk = (data[i * max_batch:(i * max_batch) + max_batch])
        payload = make_payload(data_chunk, media_player)
        submit_to_listenbrainz(payload, api_token, timeout)
    print('Done')
