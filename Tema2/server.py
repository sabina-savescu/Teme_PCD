#!/usr/bin/env python
import json

import asyncio
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import websockets
import logging

import cfg
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
            print('Found {0} documents'.format(document_list.__len__()))

            ip_list=[]
            for doc in document_list:
                doc_id=doc.get('id')
                doc_link = collection_link + '/docs/' + doc_id
                response = client.ReadItem(doc_link)
                ip=response.get('ip')
                port=response.get('port')
                print('Document read by Id {0}'.format(doc_id))
                print('IP: {0}'.format(ip))
                print('PORT: {0}'.format(port))
                in_use=OPTION['value']
                ip_list.append((ip,port,in_use))

        except errors.HTTPFailure as e:
            print('\nget_ip_list has caught an error. {0}'.format(e.message))

        finally:
            return ip_list


logging.basicConfig()

STATE = {'value': 0}
USERS = set()
OPTION = {'value':"No"}

def state_event():
    return json.dumps({'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})


async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_users():
    if USERS:       # asyncio.wait doesn't accept an empty list
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
            if data['action'] == 'options':
                rows = get_ip_list()
                STATE['value'] = rows
                await notify_state()
            elif data['action'] == 'select':
                #select item in list which is not in use
                OPTION['value']="Yes"
                rows = get_ip_list()
                STATE['value'] = rows
                await notify_state()
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregister(websocket)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, 'localhost', 8081))
asyncio.get_event_loop().run_forever()