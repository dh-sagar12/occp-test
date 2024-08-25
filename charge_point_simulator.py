import asyncio
import logging
from datetime import datetime
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

logging.basicConfig(level=logging.INFO)

class ChargePoint(cp):
    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="Wallbox XYZ",
            charge_point_vendor="anewone"
        )
        response = await self.call(request)
        if response.status == RegistrationStatus.accepted:
            logging.info("Connected to central system.")

    async def start_transaction(self, id_tag):
        request = call.StartTransactionPayload(
            connector_id=1,
            id_tag=id_tag,
            meter_start=0,
            timestamp=datetime.utcnow().isoformat()
        )
        response = await self.call(request)
        return response.transaction_id

    async def send_meter_values(self, transaction_id):
        for i in range(1, 101, 1):
            request = call.MeterValuesPayload(
                connector_id=1,
                transaction_id=transaction_id,
                meter_value=[{
                    "timestamp": datetime.utcnow().isoformat(),
                    "sampledValue": [{
                        "value": str(i),
                        "context": "Sample.Periodic",
                        "format": "Raw",
                        "measurand": "Energy.Active.Import.Register",
                        "unit": "Wh"
                    }]
                }]
            )
            await self.call(request)
            await asyncio.sleep(5)

    async def stop_transaction(self, transaction_id):
        request = call.StopTransactionPayload(
            transaction_id=transaction_id,
            meter_stop=100,
            timestamp=datetime.utcnow().isoformat()
        )
        await self.call(request)

async def main():
    async with websockets.connect(
        'ws://localhost:9000/1',
        subprotocols=['ocpp1.6']
    ) as ws:
        cp = ChargePoint('1', ws)
        await asyncio.gather(
            cp.start(),
            cp.send_boot_notification(),
            simulate_charging_session(cp)
        )

async def simulate_charging_session(cp):
    # Simulate a charging session
    transaction_id = await cp.start_transaction("test_user")
    await cp.send_meter_values(transaction_id)
    await cp.stop_transaction(transaction_id)

if __name__ == '__main__':
    asyncio.run(main())