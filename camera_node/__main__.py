import asyncio
import argparse
import aiohttp
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription
from .stream_manager import CameraStreamTrack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("camera_node")

async def run(server_url, camera_index):
    pc = RTCPeerConnection()
    track = CameraStreamTrack(camera_index)
    pc.addTrack(track)

    logger.info(f"Connecting to server at {server_url}")

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # send offer to server
    payload = {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
        "camera_id": camera_index
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=payload) as resp:
            if resp.status == 200:
                res_data = await resp.json()
                answer = RTCSessionDescription(sdp=res_data["sdp"], type=res_data["type"])
                await pc.setRemoteDescription(answer)
                logger.info("Connection established! Streaming video...")
            else:
                logger.error(f"Failed to connect: {resp.status} {await resp.text()}")
                await pc.close()
                return

    # keep running until connection fails
    while True:
        await asyncio.sleep(1)
        if pc.connectionState == "failed":
            logger.error("Connection failed")
            break

    await pc.close()
    track.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camera Node (Push)")
    parser.add_argument("--server", default="http://localhost:8000/offer", help="Server URL")
    parser.add_argument("--camera", type=int, default=0, help="Camera Index")
    args = parser.parse_args()

    asyncio.run(run(args.server, args.camera))
