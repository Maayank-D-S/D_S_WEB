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
from livekit.plugins import deepgram, cartesia
from Chatbot.bot import generate_response

# Load env
load_dotenv()
deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
cartesia_api_key = os.getenv("CARTESIA_API_KEY")

logger = logging.getLogger("transcribe")
logging.basicConfig(level=logging.DEBUG)

# === Warm-up ===
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

warm_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
warm_llm.invoke([HumanMessage(content="Hi!")])  # warm up the model


def fetch_response(user_input):
    logger.debug(f"[fetch_response] User input: {user_input}")
    history = [{"role": "user", "content": user_input}]
    result = generate_response("Ramvan Villas", history, voice_mode=True)
    logger.debug(f"[fetch_response] Response from bot: {result}")
    return result["text"]


async def entrypoint(ctx: JobContext):
    logger.info(f" Starting transcriber for room: {ctx.room.name}")

    stt_impl = deepgram.STT(
        model="nova-3-general",
        api_key=deepgram_api_key,
        language="en",
        interim_results=True,
        punctuate=True,
        no_delay=True,
        filler_words=True,
        profanity_filter=True,
        numerals=True,
    )
    tts = cartesia.TTS(
        api_key=cartesia_api_key,
        model="sonic-2",
        language="en",
        voice="f91ab3e6-5071-4e15-b016-cde6f2bcd222",
        encoding="pcm_s16le",
        sample_rate=24000,
    )

    audio_src = rtc.AudioSource(sample_rate=24000, num_channels=1)
    audio_track = rtc.LocalAudioTrack.create_audio_track("bot-tts", audio_src)

    async def transcribe_track(participant: rtc.RemoteParticipant, track: rtc.Track):
        logger.info(f" Starting transcription for: {participant.identity}")
        audio_stream = rtc.AudioStream(track)
        stt_stream = stt_impl.stream()

        async def _handle_audio_stream():
            async for ev in audio_stream:
                stt_stream.push_frame(ev.frame)

        async def _handle_transcription_output():
            async for ev in stt_stream:
                if ev.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
                    user_query = ev.alternatives[0].text.strip()
                    if not user_query:
                        logger.warning("Empty user query, skipping.")
                        continue

                    logger.info(f" User query: {participant.identity}: {user_query}")

                    # Use asyncio.create_task to allow overlap
                    async def respond_and_speak():
                        response_text = await asyncio.to_thread(
                            fetch_response, user_query
                        )
                        logger.info(f" Bot response: {response_text}")

                        synth_stream = tts.synthesize(response_text)
                        async for chunk in synth_stream:
                            await audio_src.capture_frame(chunk.frame)

                    asyncio.create_task(respond_and_speak())

        await asyncio.gather(
            _handle_audio_stream(),
            _handle_transcription_output(),
        )

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            asyncio.create_task(transcribe_track(participant, track))

    @ctx.room.on("participant_joined")
    def on_participant_joined(participant):
        logger.info(f" Participant joined: {participant.identity}")

    @ctx.room.on("track_published")
    def on_track_published(publication, participant):
        logger.info(f" Track published from {participant.identity}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    await ctx.room.local_participant.publish_track(audio_track)
    logger.info(" Ready and listening...")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
