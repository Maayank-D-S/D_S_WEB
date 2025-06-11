import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    stt,
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from livekit.plugins import assemblyai
from krupal_chatbot.chatbot import fetch_response

load_dotenv()

logger = logging.getLogger("transcribe")
logging.basicConfig(level=logging.INFO)

async def speak_response(response_text: str, room: rtc.Room):
    # Placeholder TTS logic
    # Convert response_text to audio frames and publish to the room
    # You must implement this with your TTS system.
    # logger.info(f"Speaking response: {response_text}")

    # Example if you have raw PCM frames
    # Create a LocalAudioTrack
    # You could use a generator that yields audio frames
    # and write them into the LiveKit audio track.

    # Example:
    # audio_stream = your_tts_to_audio_stream(response_text)
    # audio_track = rtc.LocalAudioTrack.create_audio_track("response", audio_stream)
    # await room.local_participant.publish_track(audio_track)

    pass  # Replace with real implementation

async def entrypoint(ctx: JobContext):
    logger.info(f"Starting transcriber (speech to text) example, room: {ctx.room.name}")

    stt_impl = assemblyai.STT()

    async def transcribe_track(participant: rtc.RemoteParticipant, track: rtc.Track):
        logger.info(f"Started transcribing track for participant: {participant.identity}")
        audio_stream = rtc.AudioStream(track)
        stt_stream = stt_impl.stream()

        async def _handle_audio_stream():
            async for ev in audio_stream:
                
                stt_stream.push_frame(ev.frame)

        async def _handle_transcription_output():
            async for ev in stt_stream:
                # logger.debug(f"Received transcription event: {ev}")
                if ev.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
                    user_query = ev.alternatives[0].text
                    logger.info(f"query: {participant.identity}: {user_query}")
                    
                    # Get AI response
                    response_text = await fetch_response(user_query)
                    logger.info(f"Response: {response_text}")
                    print(f"Response: {response_text}")

                    
                    
        await asyncio.gather(
            _handle_audio_stream(),
            _handle_transcription_output(),
        )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            asyncio.create_task(transcribe_track(participant, track))

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
