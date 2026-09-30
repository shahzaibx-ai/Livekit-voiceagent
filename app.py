import html
import uuid
import gradio as gr

from dotenv import load_dotenv
from livekit import api
import os


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv(".env")

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

AGENT_NAME = "my-agent"


# ---------------------------------------------------------
# Create LiveKit session
# ---------------------------------------------------------

def create_voice_session(user_name, room_name):

    if not LIVEKIT_URL:
        return """
        <div class="error-box">
            LIVEKIT_URL is missing from your .env file.
        </div>
        """

    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return """
        <div class="error-box">
            LIVEKIT_API_KEY or LIVEKIT_API_SECRET is missing from your .env file.
        </div>
        """

    user_name = (user_name or "").strip()

    if not user_name:
        user_name = "Guest"

    room_name = (room_name or "").strip()

    # Empty room name = create a new unique room
    if not room_name:
        room_name = f"voice-room-{uuid.uuid4().hex[:8]}"

    participant_identity = f"user-{uuid.uuid4().hex[:8]}"

    try:

        token = (
            api.AccessToken(
                LIVEKIT_API_KEY,
                LIVEKIT_API_SECRET,
            )
            .with_identity(participant_identity)
            .with_name(user_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                )
            )
            .with_room_config(
                api.RoomConfiguration(
                    agents=[
                        api.RoomAgentDispatch(
                            agent_name=AGENT_NAME
                        )
                    ]
                )
            )
            .to_jwt()
        )

    except Exception as e:

        return f"""
        <div class="error-box">
            <b>Token creation failed</b><br><br>
            {html.escape(str(e))}
        </div>
        """

    safe_user = html.escape(user_name)
    safe_room = html.escape(room_name)
    safe_url = html.escape(LIVEKIT_URL)
    safe_token = html.escape(token, quote=True)

    return f"""
    <div
        id="livekit-voice-ui"
        class="voice-card"
        data-livekit-url="{safe_url}"
        data-livekit-token="{safe_token}"
    >

        <div class="voice-header">

            <div class="voice-title">
                🎙️ LiveKit Voice Agent
            </div>

            <div class="voice-subtitle">
                Talk with your AI assistant
            </div>

        </div>


        <div class="session-info">

            <div>
                <span class="label">User</span>
                <span class="value">{safe_user}</span>
            </div>

            <div>
                <span class="label">Room</span>
                <span class="value">{safe_room}</span>
            </div>

        </div>


        <div id="lk-status" class="status">
            Ready. Click Connect.
        </div>


        <div class="voice-buttons">

            <button
                id="lk-connect"
                type="button"
                data-action="connect"
                class="primary-btn"
            >
                Connect
            </button>


            <button
                id="lk-mute"
                type="button"
                data-action="mute"
                class="secondary-btn"
                disabled
            >
                Mute
            </button>


            <button
                id="lk-audio"
                type="button"
                data-action="audio"
                class="secondary-btn"
                disabled
            >
                Enable Audio
            </button>


            <button
                id="lk-disconnect"
                type="button"
                data-action="disconnect"
                class="danger-btn"
                disabled
            >
                Disconnect
            </button>

        </div>


        <div id="lk-mic-visualizer">

            <div class="visualizer-title">
                🎙️ Microphone Input
            </div>

            <canvas id="lk-mic-canvas"></canvas>

            <div id="lk-mic-level">
                Waiting for microphone...
            </div>

        </div>


        <div id="lk-audio-container"></div>


        <div class="help-text">
            Allow microphone permission when your browser asks.
        </div>

    </div>
    """


# ---------------------------------------------------------
# Browser JavaScript
# ---------------------------------------------------------

APP_JS = r"""
function() {

    console.log("LiveKit Gradio UI loaded");

    let room = null;
    let micEnabled = true;

    let audioContext = null;
    let analyser = null;
    let visualizerSource = null;
    let animationFrame = null;


    function getRoot() {

        return document.getElementById(
            "livekit-voice-ui"
        );
    }


    function getStatus() {

        return document.getElementById(
            "lk-status"
        );
    }


    function setStatus(message) {

        const status = getStatus();

        if (status) {
            status.textContent = message;
        }

        console.log(
            "[LiveKit]",
            message
        );
    }


    function setButtonState(id, enabled) {

        const button =
            document.getElementById(id);

        if (button) {
            button.disabled = !enabled;
        }
    }


    async function waitForLiveKit() {

        if (window.LivekitClient) {
            return window.LivekitClient;
        }


        setStatus(
            "Loading LiveKit JavaScript SDK..."
        );


        for (
            let attempt = 0;
            attempt < 100;
            attempt++
        ) {

            if (window.LivekitClient) {

                console.log(
                    "LiveKit JavaScript SDK loaded."
                );

                return window.LivekitClient;
            }


            await new Promise(
                resolve =>
                    setTimeout(resolve, 100)
            );
        }


        throw new Error(
            "LiveKit JavaScript SDK did not load."
        );
    }


    function attachAudioTrack(track) {

        if (!track) {
            return;
        }


        try {

            const container =
                document.getElementById(
                    "lk-audio-container"
                );


            if (!container) {
                return;
            }


            const element =
                track.attach();


            element.autoplay = true;
            element.controls = false;


            container.appendChild(
                element
            );


            console.log(
                "AI audio track attached."
            );


        } catch (error) {

            console.error(
                "Audio attach error:",
                error
            );


            setStatus(
                "Audio error: " +
                error.message
            );
        }
    }


    function stopMicVisualizer() {

        if (animationFrame) {

            cancelAnimationFrame(
                animationFrame
            );

            animationFrame = null;
        }


        if (visualizerSource) {

            try {
                visualizerSource.disconnect();
            } catch (_) {
            }

            visualizerSource = null;
        }


        if (analyser) {

            try {
                analyser.disconnect();
            } catch (_) {
            }

            analyser = null;
        }


        if (audioContext) {

            try {
                audioContext.close();
            } catch (_) {
            }

            audioContext = null;
        }


        const canvas =
            document.getElementById(
                "lk-mic-canvas"
            );


        if (canvas) {

            const ctx =
                canvas.getContext("2d");


            ctx.clearRect(
                0,
                0,
                canvas.width,
                canvas.height
            );
        }


        const level =
            document.getElementById(
                "lk-mic-level"
            );


        if (level) {

            level.textContent =
                "Microphone stopped.";
        }
    }


    async function startMicVisualizer(
        microphonePublication
    ) {

        try {

            if (
                !microphonePublication ||
                !microphonePublication.track
            ) {

                console.log(
                    "Microphone publication not ready."
                );

                return;
            }


            const mediaStreamTrack =
                microphonePublication
                    .track
                    .mediaStreamTrack;


            if (!mediaStreamTrack) {

                console.log(
                    "Microphone MediaStreamTrack unavailable."
                );

                return;
            }


            stopMicVisualizer();


            const mediaStream =
                new MediaStream([
                    mediaStreamTrack
                ]);


            const AudioContextClass =
                window.AudioContext ||
                window.webkitAudioContext;


            if (!AudioContextClass) {

                throw new Error(
                    "Web Audio API is not available."
                );
            }


            audioContext =
                new AudioContextClass();


            await audioContext.resume();


            analyser =
                audioContext.createAnalyser();


            analyser.fftSize = 1024;
            analyser.smoothingTimeConstant = 0.75;


            visualizerSource =
                audioContext.createMediaStreamSource(
                    mediaStream
                );


            visualizerSource.connect(
                analyser
            );


            const canvas =
                document.getElementById(
                    "lk-mic-canvas"
                );


            const level =
                document.getElementById(
                    "lk-mic-level"
                );


            if (!canvas) {
                return;
            }


            const ctx =
                canvas.getContext("2d");


            const bufferLength =
                analyser.fftSize;


            const dataArray =
                new Uint8Array(
                    bufferLength
                );


            function drawWave() {

                animationFrame =
                    requestAnimationFrame(
                        drawWave
                    );


                analyser.getByteTimeDomainData(
                    dataArray
                );


                const width =
                    canvas.clientWidth ||
                    600;


                const height =
                    canvas.clientHeight ||
                    120;


                const ratio =
                    window.devicePixelRatio ||
                    1;


                canvas.width =
                    width * ratio;


                canvas.height =
                    height * ratio;


                ctx.setTransform(
                    ratio,
                    0,
                    0,
                    ratio,
                    0,
                    0
                );


                ctx.clearRect(
                    0,
                    0,
                    width,
                    height
                );


                ctx.beginPath();

                ctx.strokeStyle =
                    "rgba(127,127,127,0.25)";

                ctx.lineWidth = 1;


                ctx.moveTo(
                    0,
                    height / 2
                );


                ctx.lineTo(
                    width,
                    height / 2
                );


                ctx.stroke();


                ctx.beginPath();

                ctx.strokeStyle =
                    "#2563eb";

                ctx.lineWidth = 3;


                const sliceWidth =
                    width / bufferLength;


                let x = 0;
                let totalEnergy = 0;


                for (
                    let i = 0;
                    i < bufferLength;
                    i++
                ) {

                    const value =
                        dataArray[i] / 128.0;


                    const y =
                        value * height / 2;


                    totalEnergy +=
                        Math.abs(
                            value - 1
                        );


                    if (i === 0) {

                        ctx.moveTo(
                            x,
                            y
                        );

                    } else {

                        ctx.lineTo(
                            x,
                            y
                        );
                    }


                    x += sliceWidth;
                }


                ctx.stroke();


                const average =
                    totalEnergy /
                    bufferLength;


                const percentage =
                    Math.min(
                        100,
                        Math.round(
                            average * 100
                        )
                    );


                if (level) {

                    if (!micEnabled) {

                        level.textContent =
                            "Microphone muted.";

                    } else if (
                        percentage > 3
                    ) {

                        level.textContent =
                            "Microphone active • Audio level " +
                            percentage +
                            "%";

                    } else {

                        level.textContent =
                            "Microphone connected • Speak now";
                    }
                }
            }


            drawWave();


            console.log(
                "Microphone waveform started."
            );


        } catch (error) {

            console.error(
                "Microphone visualizer error:",
                error
            );


            const level =
                document.getElementById(
                    "lk-mic-level"
                );


            if (level) {

                level.textContent =
                    "Microphone connected, but visualizer unavailable.";
            }
        }
    }


    async function connectLiveKit() {

        console.log(
            "Connect button clicked."
        );


        if (room) {
            return;
        }


        const root =
            getRoot();


        if (!root) {

            setStatus(
                "Voice session data not found."
            );

            return;
        }


        const url =
            root.dataset.livekitUrl;


        const token =
            root.dataset.livekitToken;


        if (!url) {

            setStatus(
                "LiveKit URL is missing."
            );

            return;
        }


        if (!token) {

            setStatus(
                "LiveKit token is missing."
            );

            return;
        }


        try {

            const LivekitClient =
                await waitForLiveKit();


            const {
                Room,
                RoomEvent,
                Track
            } = LivekitClient;


            setStatus(
                "Requesting microphone permission..."
            );


            await navigator
                .mediaDevices
                .getUserMedia({
                    audio: true
                });


            setStatus(
                "Connecting to LiveKit..."
            );


            room =
                new Room({
                    adaptiveStream: true,
                    dynacast: true
                });


            room.on(
                RoomEvent.LocalTrackPublished,
                async (publication) => {

                    console.log(
                        "LOCAL TRACK PUBLISHED:",
                        publication.kind,
                        publication.source
                    );


                    if (
                        publication.source ===
                        Track.Source.Microphone
                    ) {

                        setStatus(
                            "Microphone connected. Audio is being sent to LiveKit."
                        );


                        await startMicVisualizer(
                            publication
                        );
                    }
                }
            );


            room.on(
                RoomEvent.LocalTrackUnpublished,
                (publication) => {

                    console.log(
                        "LOCAL TRACK UNPUBLISHED:",
                        publication.kind,
                        publication.source
                    );
                }
            );


            room.on(
                RoomEvent.TrackSubscribed,
                (
                    track,
                    publication,
                    participant
                ) => {

                    console.log(
                        "REMOTE TRACK:",
                        track.kind,
                        participant.identity
                    );


                    if (
                        track.kind === "audio"
                    ) {

                        attachAudioTrack(
                            track
                        );


                        setStatus(
                            "AI assistant audio connected."
                        );
                    }
                }
            );


            room.on(
                RoomEvent.TrackUnsubscribed,
                (track) => {

                    try {
                        track.detach();
                    } catch (error) {
                        console.error(error);
                    }
                }
            );


            room.on(
                RoomEvent.ParticipantConnected,
                (participant) => {

                    console.log(
                        "PARTICIPANT CONNECTED:",
                        participant.identity
                    );


                    setStatus(
                        "AI assistant connected. Microphone is ready."
                    );
                }
            );


            room.on(
                RoomEvent.ParticipantDisconnected,
                (participant) => {

                    console.log(
                        "PARTICIPANT DISCONNECTED:",
                        participant.identity
                    );
                }
            );


            room.on(
                RoomEvent.MediaDevicesError,
                (error) => {

                    console.error(
                        "MEDIA DEVICE ERROR:",
                        error
                    );


                    setStatus(
                        "Microphone error: " +
                        error.message
                    );
                }
            );


            room.on(
                RoomEvent.AudioPlaybackStatusChanged,
                () => {

                    if (
                        room &&
                        !room.canPlaybackAudio
                    ) {

                        setStatus(
                            "Connected. Click Enable Audio for AI voice output."
                        );

                    } else {

                        setStatus(
                            "AI audio playback is enabled."
                        );
                    }


                    setButtonState(
                        "lk-audio",
                        true
                    );
                }
            );


            room.on(
                RoomEvent.Disconnected,
                () => {

                    console.log(
                        "Disconnected from LiveKit."
                    );


                    stopMicVisualizer();


                    room = null;


                    setButtonState(
                        "lk-connect",
                        true
                    );


                    setButtonState(
                        "lk-mute",
                        false
                    );


                    setButtonState(
                        "lk-audio",
                        false
                    );


                    setButtonState(
                        "lk-disconnect",
                        false
                    );


                    setStatus(
                        "Disconnected."
                    );
                }
            );


            await room.connect(
                url,
                token
            );


            console.log(
                "CONNECTED TO ROOM:",
                room.name
            );


            setButtonState(
                "lk-connect",
                false
            );


            setButtonState(
                "lk-mute",
                true
            );


            setButtonState(
                "lk-audio",
                true
            );


            setButtonState(
                "lk-disconnect",
                true
            );


            setStatus(
                "Connected. Publishing microphone..."
            );


            const microphonePublication =
                await room
                    .localParticipant
                    .setMicrophoneEnabled(
                        true
                    );


            if (!microphonePublication) {

                throw new Error(
                    "LiveKit did not create a microphone publication."
                );
            }


            console.log(
                "MICROPHONE PUBLICATION:",
                microphonePublication
            );


            console.log(
                "MICROPHONE ENABLED:",
                room
                    .localParticipant
                    .isMicrophoneEnabled
            );


            micEnabled = true;


            await startMicVisualizer(
                microphonePublication
            );


            setStatus(
                "Microphone is live. Click Enable Audio for AI voice output."
            );


            room.remoteParticipants.forEach(
                (participant) => {

                    participant
                        .trackPublications
                        .forEach(
                            (publication) => {

                                if (
                                    publication.isSubscribed &&
                                    publication.track &&
                                    publication.track.kind ===
                                    "audio"
                                ) {

                                    attachAudioTrack(
                                        publication.track
                                    );
                                }
                            }
                        );
                }
            );


        } catch (error) {

            console.error(
                "LIVEKIT CONNECTION ERROR:",
                error
            );


            setStatus(
                "Microphone/connection failed: " +
                error.message
            );


            stopMicVisualizer();


            if (room) {

                try {
                    await room.disconnect();
                } catch (_) {
                }
            }


            room = null;


            setButtonState(
                "lk-connect",
                true
            );


            setButtonState(
                "lk-mute",
                false
            );


            setButtonState(
                "lk-audio",
                false
            );


            setButtonState(
                "lk-disconnect",
                false
            );
        }
    }


    async function toggleMute() {

        if (!room) {
            return;
        }


        try {

            micEnabled =
                !micEnabled;


            await room
                .localParticipant
                .setMicrophoneEnabled(
                    micEnabled
                );


            const button =
                document.getElementById(
                    "lk-mute"
                );


            if (button) {

                button.textContent =
                    micEnabled
                    ? "Mute"
                    : "Unmute";
            }


            setStatus(
                micEnabled
                ? "Microphone enabled."
                : "Microphone muted."
            );


            const level =
                document.getElementById(
                    "lk-mic-level"
                );


            if (level) {

                level.textContent =
                    micEnabled
                    ? "Microphone enabled."
                    : "Microphone muted.";
            }


        } catch (error) {

            console.error(
                "Mute error:",
                error
            );


            setStatus(
                "Microphone error: " +
                error.message
            );
        }
    }


    async function enableAudio() {

        console.log(
            "Enable Audio button clicked."
        );


        if (!room) {

            setStatus(
                "Connect to LiveKit first."
            );

            return;
        }


        try {

            setStatus(
                "Enabling AI audio..."
            );


            /*
             * This must be called from
             * the actual user click.
             */

            await room.startAudio();


            setStatus(
                "AI audio enabled. Speak to the assistant."
            );


            console.log(
                "AI audio playback enabled."
            );


        } catch (error) {

            console.error(
                "ENABLE AUDIO ERROR:",
                error
            );


            setStatus(
                "Could not enable AI audio: " +
                error.message
            );
        }
    }


    async function disconnectLiveKit() {

        if (!room) {
            return;
        }


        try {

            stopMicVisualizer();


            await room.disconnect();

        } catch (error) {

            console.error(
                "Disconnect error:",
                error
            );
        }


        const container =
            document.getElementById(
                "lk-audio-container"
            );


        if (container) {
            container.innerHTML = "";
        }


        room = null;
    }


    /*
     * Button event handling.
     */

    document.addEventListener(
        "click",
        async function(event) {

            const button =
                event.target.closest(
                    "button[data-action]"
                );


            if (!button) {
                return;
            }


            const action =
                button.dataset.action;


            console.log(
                "Button action:",
                action
            );


            if (action === "connect") {

                await connectLiveKit();

            } else if (action === "mute") {

                await toggleMute();

            } else if (action === "audio") {

                await enableAudio();

            } else if (action === "disconnect") {

                await disconnectLiveKit();
            }
        }
    );


    console.log(
        "LiveKit button handlers registered."
    );
}
"""


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

APP_CSS = """

.voice-card {
    max-width: 760px;
    margin: 20px auto;
    padding: 28px;
    border-radius: 20px;
    border: 1px solid var(--block-border-color);
    background: var(--body-background-fill);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}


.voice-header {
    text-align: center;
    margin-bottom: 22px;
}


.voice-title {
    font-size: 28px;
    font-weight: 700;
}


.voice-subtitle {
    margin-top: 6px;
    opacity: 0.7;
}


.session-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 18px;
}


.session-info > div {
    padding: 14px;
    border-radius: 12px;
    background: rgba(127, 127, 127, 0.08);
}


.label {
    display: block;
    font-size: 12px;
    opacity: 0.65;
    margin-bottom: 4px;
}


.value {
    display: block;
    font-weight: 600;
    word-break: break-word;
}


.status {
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 18px;
    background: rgba(127, 127, 127, 0.10);
}


.voice-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
}


.voice-buttons button {
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    cursor: pointer;
    font-weight: 600;
}


.voice-buttons button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}


.primary-btn {
    background: #2563eb;
    color: white;
}


.secondary-btn {
    background: #64748b;
    color: white;
}


.danger-btn {
    background: #dc2626;
    color: white;
}


.help-text {
    margin-top: 18px;
    text-align: center;
    font-size: 13px;
    opacity: 0.65;
}


.error-box {
    padding: 18px;
    border-radius: 12px;
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}


/* Microphone visualizer */

#lk-mic-visualizer {
    margin-top: 20px;
    padding: 18px;
    border-radius: 16px;
    background: rgba(127, 127, 127, 0.08);
    border: 1px solid rgba(127, 127, 127, 0.18);
}


.visualizer-title {
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
}


#lk-mic-canvas {
    display: block;
    width: 100%;
    height: 120px;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.04);
}


#lk-mic-level {
    text-align: center;
    margin-top: 10px;
    font-size: 13px;
    opacity: 0.7;
}


#lk-audio-container {
    display: none;
}


@media (max-width: 600px) {

    .session-info {
        grid-template-columns: 1fr;
    }

    .voice-card {
        padding: 18px;
    }

}
"""


# ---------------------------------------------------------
# Gradio Interface
# ---------------------------------------------------------

with gr.Blocks(
    title="LiveKit Voice AI Assistant",
    js=APP_JS,
    css=APP_CSS,

    head="""
    <script
        src="https://cdn.jsdelivr.net/npm/livekit-client@2.22.3/dist/livekit-client.umd.min.js">
    </script>
    """
) as demo:

    gr.Markdown(
        """
        # 🎙️ LiveKit Voice AI Assistant

        Connect your microphone and talk to your LiveKit AI voice agent.
        """
    )


    with gr.Row():

        user_name = gr.Textbox(
            label="Your Name",
            placeholder="Enter your name",
            value="Guest",
        )


        room_name = gr.Textbox(
            label="Room Name",
            placeholder="Leave empty for a new room",
        )


    create_button = gr.Button(
        "Create Voice Session",
        variant="primary",
    )


    voice_ui = gr.HTML(
        """
        <div style="
            padding:25px;
            text-align:center;
            border:1px dashed #999;
            border-radius:15px;
            opacity:0.8;
        ">
            Enter your name and click
            <b>Create Voice Session</b>.
        </div>
        """
    )


    create_button.click(
        fn=create_voice_session,
        inputs=[
            user_name,
            room_name,
        ],
        outputs=voice_ui,
    )


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
    )