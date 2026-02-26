import { useState, useRef } from "react";
import { Search, Loader2, Mic, MicOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FlipWords } from "@/components/ui/flip-words";

const ASSEMBLYAI_KEY = import.meta.env.VITE_ASSEMBLYAI_KEY;
const SAMPLE_RATE = 16000;

const HeroSection = ({ title, onTitleChange, onVerify, isLoading }) => {
    const [isListening, setIsListening] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const wsRef = useRef(null);
    const audioCtxRef = useRef(null);
    const processorRef = useRef(null);
    const streamRef = useRef(null);
    const recognitionRef = useRef(null);
    const silenceTimerRef = useRef(null);

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && title.trim() && !isLoading) onVerify();
    };

    const stopListening = () => {
        clearTimeout(silenceTimerRef.current);
        processorRef.current?.disconnect();
        audioCtxRef.current?.close();
        streamRef.current?.getTracks().forEach((t) => t.stop());
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ terminate_session: true }));
        }
        wsRef.current?.close();
        wsRef.current = null;
        audioCtxRef.current = null;
        processorRef.current = null;
        streamRef.current = null;
        recognitionRef.current?.stop();
        recognitionRef.current = null;
        setIsListening(false);
        setIsConnecting(false);
    };

    // After transcript arrives, wait 3s of silence then auto-verify
    const scheduleAutoVerify = (text, verifyFn) => {
        clearTimeout(silenceTimerRef.current);
        if (!text.trim()) return;
        silenceTimerRef.current = setTimeout(() => {
            stopListening();
            verifyFn();
        }, 3000);
    };

    // Improved native Web Speech API — continuous, accumulates finals
    const startNativeSpeech = () => {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { alert("Voice input not supported in this browser."); return; }
        const r = new SR();
        r.lang = "en-IN";           // Indian English — better for local accents
        r.interimResults = true;
        r.continuous = true;        // keep mic open between phrases
        r.maxAlternatives = 3;      // pick best of 3 alternatives
        recognitionRef.current = r;

        let finalText = "";

        r.onstart = () => { setIsConnecting(false); setIsListening(true); };
        r.onend = () => {
            // auto-restart unless user stopped manually
            if (recognitionRef.current) {
                try { r.start(); } catch { /* already stopped */ }
            } else {
                setIsListening(false);
            }
        };
        r.onerror = (ev) => {
            if (ev.error === "no-speech") return; // ignore silence
            setIsListening(false);
        };
        r.onresult = (e) => {
            let interim = "";
            for (let i = e.resultIndex; i < e.results.length; i++) {
                // pick highest-confidence alternative
                let best = e.results[i][0].transcript;
                for (let j = 1; j < e.results[i].length; j++) {
                    if (e.results[i][j].confidence > e.results[i][0].confidence)
                        best = e.results[i][j].transcript;
                }
                if (e.results[i].isFinal) {
                    finalText += best + " ";
                    scheduleAutoVerify(finalText.trim(), onVerify); // only on finals
                } else {
                    interim = best;
                }
            }
            onTitleChange((finalText + interim).trim());
        };
        r.start();
    };

    const handleMic = async () => {
        if (isListening || isConnecting) { stopListening(); return; }
        setIsConnecting(true);

        try {
            const tokenRes = await fetch("https://api.assemblyai.com/v2/realtime/token", {
                method: "POST",
                headers: { authorization: ASSEMBLYAI_KEY, "content-type": "application/json" },
                body: JSON.stringify({ expires_in: 480 }),
            });

            if (!tokenRes.ok) throw new Error("Token fetch failed");
            const { token } = await tokenRes.json();
            if (!token) throw new Error("No token returned");

            const ws = new WebSocket(
                `wss://api.assemblyai.com/v2/realtime/ws?sample_rate=${SAMPLE_RATE}&token=${token}`
            );
            wsRef.current = ws;
            ws.onerror = () => { stopListening(); startNativeSpeech(); };
            ws.onclose = () => setIsListening(false);
            ws.onmessage = (msg) => {
                const data = JSON.parse(msg.data);
                if (data.text) {
                    onTitleChange(data.text);
                    scheduleAutoVerify(data.text, onVerify);
                }
            };
            ws.onopen = async () => {
                // High-quality audio constraints
                const stream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        channelCount: 1,
                        sampleRate: SAMPLE_RATE,
                    }
                });
                streamRef.current = stream;
                const audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE });
                audioCtxRef.current = audioCtx;
                const source = audioCtx.createMediaStreamSource(stream);
                const processor = audioCtx.createScriptProcessor(2048, 1, 1); // smaller buffer = lower latency
                processorRef.current = processor;
                processor.onaudioprocess = (e) => {
                    if (ws.readyState !== WebSocket.OPEN) return;
                    const f32 = e.inputBuffer.getChannelData(0);
                    const i16 = new Int16Array(f32.length);
                    for (let i = 0; i < f32.length; i++)
                        i16[i] = Math.max(-32768, Math.min(32767, f32[i] * 32768));
                    ws.send(i16.buffer);
                };
                source.connect(processor);
                processor.connect(audioCtx.destination);
                setIsConnecting(false);
                setIsListening(true);
            };
        } catch {
            // AssemblyAI failed → fall back to native Web Speech API
            stopListening();
            startNativeSpeech();
        }
    };

    const flipWords = ["Similarity", "Compliance", "Originality"];
    const micBusy = isListening || isConnecting;

    return (
        <section className="py-40 md:py-48 text-center">
            <div className="max-w-2xl mx-auto space-y-6">
                <h1
                    className="text-3xl md:text-4xl font-bold text-foreground tracking-tight leading-tight"
                    style={{ fontWeight: 700, letterSpacing: "-0.025em" }}
                >
                    Title <FlipWords words={flipWords} duration={1500} /> Validation System
                </h1>
                <p className="text-muted-foreground text-base md:text-lg">
                    AI-powered Title Verification and Compliance System
                </p>

                <div className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto pt-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground z-10" />
                        <Input
                            value={title}
                            onChange={(e) => onTitleChange(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Enter newspaper title to verify..."
                            className="pl-10 pr-14 h-12 rounded-full text-foreground placeholder:text-muted-foreground"
                            style={{
                                background: "rgba(255,255,255,0.15)",
                                backdropFilter: "blur(14px)",
                                WebkitBackdropFilter: "blur(14px)",
                                border: "1px solid rgba(255,255,255,0.35)",
                                boxShadow: "0 4px 24px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.4)",
                            }}
                        />
                        {/* Mic pill inside the input on the right */}
                        <button
                            type="button"
                            onClick={handleMic}
                            title={micBusy ? "Stop listening" : "Voice input"}
                            className={`absolute right-1.5 top-1/2 -translate-y-1/2 z-10 h-9 w-9 flex items-center justify-center rounded-full flex-shrink-0 transition-all ${isListening ? "animate-pulse" : ""}`}
                            style={{
                                background: isListening
                                    ? "rgba(239,68,68,0.35)"
                                    : isConnecting
                                        ? "rgba(250,189,42,0.35)"
                                        : "rgba(255,255,255,0.2)",
                                backdropFilter: "blur(10px)",
                                WebkitBackdropFilter: "blur(10px)",
                                border: isListening
                                    ? "1px solid rgba(239,68,68,0.5)"
                                    : isConnecting
                                        ? "1px solid rgba(250,189,42,0.5)"
                                        : "1px solid rgba(255,255,255,0.4)",
                                boxShadow: "0 2px 12px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.5)",
                                color: isListening ? "rgb(239,68,68)" : "inherit",
                            }}
                        >
                            {isConnecting ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin text-yellow-500" />
                            ) : isListening ? (
                                <MicOff className="w-3.5 h-3.5" />
                            ) : (
                                <Mic className="w-3.5 h-3.5 text-muted-foreground" />
                            )}
                        </button>
                    </div>

                    <Button
                        onClick={onVerify}
                        disabled={!title.trim() || isLoading}
                        className="h-12 px-8 font-semibold rounded-full text-gray-900"
                        style={{
                            background: "rgba(250, 189, 42, 0.75)",
                            backdropFilter: "blur(14px)",
                            WebkitBackdropFilter: "blur(14px)",
                            border: "1px solid rgba(252, 211, 77, 0.6)",
                            boxShadow: "0 4px 24px rgba(250, 189, 42, 0.25), inset 0 1px 0 rgba(255,255,255,0.4)",
                        }}
                    >
                        {isLoading ? (
                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Verifying</>
                        ) : (
                            "Verify Title"
                        )}
                    </Button>
                </div>
            </div>
        </section>
    );
};

export default HeroSection;
