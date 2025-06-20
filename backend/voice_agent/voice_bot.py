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

from livekit.plugins import deepgram
from Chatbot.bot import generate_response

# Load environment variables (make sure .env has DEEPGRAM_API_KEY)
load_dotenv()

# Configure logging
logger = logging.getLogger("transcribe")
logging.basicConfig(level=logging.DEBUG)  # Verbose logs


# Basic wrapper to call your chatbot logic
def fetch_response(user_input):
    logger.debug(f"[fetch_response] User input: {user_input}")
    history = [{"role": "user", "content": user_input}]
    result = generate_response("Krupal Habitat", history)
    logger.debug(f"[fetch_response] Response from bot: {result}")
    return result["text"]


async def entrypoint(ctx: JobContext):
    logger.info(f" Starting transcriber for room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info(" Connected to room with AUDIO_ONLY subscription")

    # 🧠 Init Deepgram STT
    stt_impl = deepgram.STT(model="nova-3", api_key="")
    logger.info(" Deepgram STT initialized")

    #  Create audio source and publish it once
    audio_src = rtc.AudioSource(sample_rate=24000, num_channels=1)
    audio_track = rtc.LocalAudioTrack.create_audio_track("bot-tts", audio_src)
    await ctx.room.local_participant.publish_track(audio_track)
    logger.info(" TTS Audio track published to room")

    #  Init Deepgram TTS
    tts = deepgram.TTS(
        model="aura-2-andromeda-en",
        encoding="linear16",
        sample_rate=24000,
        api_key="",
    )
    logger.info(" Deepgram TTS initialized")

    async def transcribe_track(participant: rtc.RemoteParticipant, track: rtc.Track):
        logger.info(f" Starting transcription for: {participant.identity}")
        audio_stream = rtc.AudioStream(track)
        stt_stream = stt_impl.stream()

        async def _handle_audio_stream():
            logger.debug(" Listening to incoming audio frames...")
            async for ev in audio_stream:
                logger.debug(" Received audio frame")
                stt_stream.push_frame(ev.frame)

        async def _handle_transcription_output():
            logger.debug(" Waiting for transcription results...")
            async for ev in stt_stream:
                logger.debug(f"[Deepgram Event] {ev}")
                if ev.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
                    user_query = ev.alternatives[0].text
                    logger.info(f" User query: {participant.identity}: {user_query}")

                    response_text = fetch_response(user_query)
                    logger.info(f" Bot response: {response_text}")

                    synth_stream = tts.synthesize(response_text)
                    logger.debug(" Synthesizing response...")
                    async for chunk in synth_stream:
                        logger.debug(" Sending TTS audio chunk")
                        await audio_src.capture_frame(chunk.frame)

        await asyncio.gather(
            _handle_audio_stream(),
            _handle_transcription_output(),
        )

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        logger.info(
            f"✅ [track_subscribed] Got track from {participant.identity} | Kind: {track.kind}"
        )
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(
                f" [track_subscribed] Subscribing to AUDIO from {participant.identity}"
            )
            asyncio.create_task(transcribe_track(participant, track))

    @ctx.room.on("participant_joined")
    def on_participant_joined(participant: rtc.RemoteParticipant):
        logger.info(f" [participant_joined] {participant.identity} joined the room")

    @ctx.room.on("track_published")
    def on_track_published(
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        logger.info(
            f" [track_published] From {participant.identity}, kind: {publication.kind}"
        )

    @ctx.room.on("*")
    def on_any_event(event_name, *args, **kwargs):
        logger.debug(f" [EVENT] {event_name} | args={args} kwargs={kwargs}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
