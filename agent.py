from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    AgentServer,
    AgentSession,
    Agent,
    inference,
    room_io,
    TurnHandlingOptions,
    UserInputTranscribedEvent,
)

from livekit.plugins import ai_coustics

load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )


server = AgentServer()


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(

        # -------------------------------------------------
        # Speech To Text
        # -------------------------------------------------

        stt=inference.STT(
            model="assemblyai/universal-3-5-pro",
            language="en",
            extra_kwargs={
                "min_turn_silence": 100,
                "max_turn_silence": 1000,
                "vad_threshold": 0.3,
            },
        ),

        # -------------------------------------------------
        # Language Model
        # -------------------------------------------------

        llm=inference.LLM(
            model="google/gemma-4-31b-it"
        ),

        # -------------------------------------------------
        # Text To Speech
        # -------------------------------------------------

        tts=inference.TTS(
            model="fishaudio/s2.1-pro",
            voice="fa4c9eb3dccc4806b382b40d61c6b10a",
        ),

        # -------------------------------------------------
        # Turn Detection
        # -------------------------------------------------

        turn_handling=TurnHandlingOptions(
            turn_detection="stt",
            endpointing={
                "min_delay": 0,
            },
        ),

        # -------------------------------------------------
        # Debugging
        # -------------------------------------------------

        transcription_timeout=5.0,

        # Explicit VAD configuration
        vad=inference.VAD(
            model="silero",
            activation_threshold=0.3,
        ),
    )

    # -----------------------------------------------------
    # Debug: show user speech transcription
    # -----------------------------------------------------

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(
        event: UserInputTranscribedEvent,
    ):
        print(
            "\nUSER:",
            event.transcript,
            "| final:",
            event.is_final,
            "| language:",
            event.language,
        )

    # -----------------------------------------------------
    # Debug: user speech state
    # -----------------------------------------------------

    @session.on("user_state_changed")
    def on_user_state_changed(event):
        print(
            "\nUSER STATE:",
            event.new_state
        )

    # -----------------------------------------------------
    # Debug: STT timeout
    # -----------------------------------------------------

    @session.on("user_transcription_timeout")
    def on_user_transcription_timeout(event):
        print(
            "\nSTT TIMEOUT:",
            event
        )

    # -----------------------------------------------------
    # Debug: session errors
    # -----------------------------------------------------

    @session.on("error")
    def on_session_error(event):
        print(
            "\nSESSION ERROR:",
            event
        )

    # -----------------------------------------------------
    # Start session
    # -----------------------------------------------------

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )

    # -----------------------------------------------------
    # Initial greeting
    # -----------------------------------------------------

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)