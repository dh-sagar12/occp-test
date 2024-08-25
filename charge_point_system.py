# import asyncio
# import logging
# from datetime import datetime
# import websockets
# from ocpp.routing import on
# from ocpp.v16 import ChargePoint as cp
# from ocpp.v16.enums import Action, RegistrationStatus
# from ocpp.v16 import call_result

# logging.basicConfig(level=logging.INFO)

# # Global dictionary to store charging status
# charging_status = {}

# class CentralSystem(cp):
#     @on(Action.BootNotification)
#     def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
#         return call_result.BootNotificationPayload(
#             current_time=datetime.utcnow().isoformat(),
#             interval=300,
#             status=RegistrationStatus.accepted
#         )

#     @on(Action.StartTransaction)
#     def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
#         return call_result.StartTransactionPayload(
#             transaction_id=1,
#             id_tag_info={"status": "Accepted"}
#         )

#     @on(Action.MeterValues)
#     def on_meter_values(self, connector_id, meter_value, **kwargs):
#         global charging_status
#         for value in meter_value:
#             sampled_value = value.get('sampledValue', [])
#             if sampled_value:
#                 meter_value = sampled_value[0].get('value')
#                 logging.info(f"Received meter value for {self.id}: {meter_value}%")
#                 # Update the charging status
#                 charging_status[self.id] = int(meter_value)
#         return call_result.MeterValuesPayload()

#     @on(Action.StopTransaction)
#     def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
#         logging.info(f"Transaction {transaction_id} stopped at {meter_stop}Wh")
#         # Remove the charging status when transaction stops
#         global charging_status
#         if self.id in charging_status:
#             del charging_status[self.id]
#         return call_result.StopTransactionPayload()

# async def on_connect(websocket, path):
#     """ For every new charge point that connects, create a ChargePoint instance
#     and start listening for messages.
#     """
#     try:
#         requested_protocols = websocket.request_headers['Sec-WebSocket-Protocol']
#     except KeyError:
#         logging.error("Client hasn't requested any Subprotocol. Closing Connection")
#         return await websocket.close()
    
#     if websocket.subprotocol:
#         logging.info("Protocols Matched: %s", websocket.subprotocol)
#     else:
#         logging.warning('Protocols Mismatched | Expected Subprotocols: %s, '
#                         'but client supports %s | Closing connection',
#                         websocket.available_subprotocols,
#                         requested_protocols)
#         return await websocket.close()

#     charge_point_id = path.strip('/')
#     cp = CentralSystem(charge_point_id, websocket)
    
#     # Initialize charging status for this charge point
#     global charging_status
#     charging_status[charge_point_id] = 0
    
#     await cp.start()

# async def main():
#     server = await websockets.serve(
#         on_connect,
#         '0.0.0.0',
#         9000,
#         subprotocols=['ocpp1.6']
#     )
    
#     logging.info("Server Started listening to new connections...")
#     await server.wait_closed()

# if __name__ == '__main__':
#     asyncio.run(main())

import asyncio
import logging
from datetime import datetime
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, Action
from ocpp.routing import on
from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)

# Global dictionary to store charging status
charging_status = {}

# Dictionary to store router WebSocket connections
router_connections = {}

class CentralSystem(cp):
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=300,
            status=RegistrationStatus.accepted
        )

    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        return call_result.StartTransactionPayload(
            transaction_id=1,
            id_tag_info={"status": "Accepted"}
        )

    @on(Action.MeterValues)
    def on_meter_values(self, connector_id, meter_value, **kwargs):
        global charging_status
        for value in meter_value:
            sampled_value = value.get('sampledValue', [])
            if sampled_value:
                meter_value = sampled_value[0].get('value')
                logging.info(f"Received meter value for {self.id}: {meter_value}%")
                # Update the charging status
                charging_status[self.id] = int(meter_value)
                # Send update to connected router
                asyncio.create_task(send_update_to_router(self.id, int(meter_value)))
        return call_result.MeterValuesPayload()

    @on(Action.StopTransaction)
    def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        logging.info(f"Transaction {transaction_id} stopped at {meter_stop}Wh")
        # Remove the charging status when transaction stops
        global charging_status
        if self.id in charging_status:
            del charging_status[self.id]
            # Send update to connected router
            asyncio.create_task(send_update_to_router(self.id, None))
        return call_result.StopTransactionPayload()

async def send_update_to_router(charge_point_id, status):
    logging.info(f"Sending update to router for {charge_point_id} with status: {status}")
    if charge_point_id in router_connections:
        try:
            await router_connections[charge_point_id].send_json({
                "charge_point_id": charge_point_id,
                "status": status
            })
            logging.info(f"Update sent to router for {charge_point_id}")
        except websockets.exceptions.ConnectionClosed:
            logging.error(f"Router connection closed for {charge_point_id}")
            del router_connections[charge_point_id]
    else:
        logging.warning(f"No router connection found for {charge_point_id}")


async def router_handler(websocket, path):
    print(websocket, path)
    charge_point_id = path.split('/')[-1]
    router_connections[charge_point_id] = websocket
    try:
        if charge_point_id in charging_status:
            await websocket.send_json({
                "charge_point_id": charge_point_id,
                "status": charging_status[charge_point_id]
            })
        while True:
            # Keep the connection open
            await asyncio.sleep(60)
    finally:
        if charge_point_id in router_connections:
            del router_connections[charge_point_id]

async def main():
    # Start WebSocket server for OCPP connections
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )

    # Start WebSocket server for router connections
    router_server = await websockets.serve(router_handler, '0.0.0.0', 9002)

    logging.info("Central System started. Listening for OCPP connections on port 9000 and router connections on port 9002")
    await asyncio.gather(server.wait_closed(), router_server.wait_closed())

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers['Sec-WebSocket-Protocol']
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s, '
                        'but client supports %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    cp = CentralSystem(charge_point_id, websocket)

    await cp.start()

if __name__ == '__main__':
    asyncio.run(main())