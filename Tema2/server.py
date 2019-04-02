#!/usr/bin/env python
import json

import asyncio
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import websockets
import logging

import cfg
import requests
HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
COLLECTION_ID = cfg.settings['collection_id']

database_link = 'dbs/' + DATABASE_ID
collection_link = database_link + '/colls/' + COLLECTION_ID

class IDisposable(cosmos_client.CosmosClient):
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

def get_ip_list():
    with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})) as client:
        try:
            # setup database for this sample
            try:
                client.CreateDatabase({"id": DATABASE_ID})

            except errors.HTTPFailure as e:
                if e.status_code == 409:
                    pass
                else:
                    raise errors.HTTPFailure(e.status_code)

            document_list = list(client.ReadItems(collection_link, {'maxItemCount': 10}))
            #print('Found {0} documents'.format(document_list.__len__()))

            ip_list=[]
            for doc in document_list:
                doc_id=doc.get('id')
                doc_link = collection_link + '/docs/' + doc_id
                response = client.ReadItem(doc_link)
                ip=response.get('ip')
                port=response.get('port')
                address = ip + ":" + port

                # print('Document read by Id {0}'.format(doc_id))
                # print('IP: {0}'.format(ip))
                # print('PORT: {0}'.format(port))

                in_use="No"
                if (address==OPTION['value']):
                    in_use=IN_USE['value']

                #use to create table in script
                ip_list.append((ip,port,in_use))

        except errors.HTTPFailure as e:
            print('\nget_ip_list has caught an error. {0}'.format(e.message))

        finally:
            return ip_list


logging.basicConfig()

STATE = {'value': 0}
USERS = set()
IN_USE = {'value':"No"}
OPTION = {'value':0}
RESPONSE = {'value':0}

def state_event():
    return json.dumps({'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})

async def url_response():
    message= json.dumps({'type': 'response', **RESPONSE})
    await asyncio.wait([user.send(message) for user in USERS])

async def notify_state():
    if USERS:
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_users():
    if USERS:
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

async def counter(websocket, path):

    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)

            if data['action'] == 'search' and IN_USE['value']=="Yes":
                    session = requests.Session()
                    http_proxy = "http://"+data['url']
                    proxies = {
                        "http": http_proxy
                    }
                    session.proxies = proxies

                    # Make the HTTP request through the session.
                    req = session.get("http://"+data['url'])

                    #for showing in html
                    RESPONSE['value']=str(req)
                    await url_response()

            # send data to create table rows
            if data['action'] == 'options':
                rows = get_ip_list()
                STATE['value'] = rows
                await notify_state()

            # get the selected address from client
            else:
                #print(data['action'])
                OPTION['value']=data['action']
                IN_USE['value'] = "Yes"
                rows = get_ip_list()
                STATE['value'] = rows
                await notify_state()

    finally:
        await unregister(websocket)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, 'localhost', 8081))
asyncio.get_event_loop().run_forever()