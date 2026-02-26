import { useEffect, useRef } from "react";

/**
 * Plays a short ting/chime using Web Audio API (no file needed).
 */
export const playTing = () => {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = "square";              // harsh square wave = loud beep
        osc.frequency.setValueAtTime(1000, ctx.currentTime); // 1 kHz beep
        gain.gain.setValueAtTime(1.0, ctx.currentTime);      // full volume
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.4);
        osc.onended = () => ctx.close();
    } catch { /* silently skip if Web Audio unavailable */ }
};


/**
 * Returns a readable description for an element.
 * Priority: aria-label > title > role-based text > text content.
 */
const describe = (el) => {
    if (!el || el === document.body) return null;

    const tag = el.tagName?.toLowerCase();
    const role = el.getAttribute("role");
    const ariaLabel = el.getAttribute("aria-label");
    const title = el.getAttribute("title");
    const placeholder = el.getAttribute("placeholder");
    const text = el.textContent?.trim().replace(/\s+/g, " ").slice(0, 120);

    // Explicit label wins
    if (ariaLabel) return ariaLabel;
    if (title) return title;

    // Functional descriptions for interactive elements
    if (tag === "button" || role === "button") {
        const label = text || el.getAttribute("value") || "button";
        return `${label}. Button.`;
    }
    if (tag === "input") {
        const type = el.getAttribute("type") || "text";
        if (placeholder) return `Input field: ${placeholder}`;
        return `${type} input field`;
    }
    if (tag === "a") {
        return `Link: ${text || el.getAttribute("href")}`;
    }
    if (tag === "select") return `Dropdown: ${text}`;
    if (tag === "textarea") return `Text area: ${placeholder || text}`;

    // For nav/section landmarks
    if (tag === "nav") return "Navigation bar";
    if (tag === "main") return "Main content area";
    if (tag === "section" || tag === "article") return text?.slice(0, 80) || null;

    // Headings
    if (/^h[1-6]$/.test(tag)) return `Heading: ${text}`;

    // Plain text nodes
    if (text) return text.slice(0, 100);

    // Walk up to find a parent with content
    return describe(el.parentElement);
};

export const useTalkback = (enabled) => {
    const synthRef = useRef(window.speechSynthesis);

    const speak = (msg) => {
        if (!msg) return;
        const synth = synthRef.current;
        synth.cancel();
        const utt = new SpeechSynthesisUtterance(msg);
        utt.lang = "en-IN";
        utt.rate = 1.1;
        utt.pitch = 1;
        // prefer a natural-sounding voice
        const voices = synth.getVoices();
        const preferred = voices.find(
            (v) => v.lang.startsWith("en") && v.localService
        ) || voices.find((v) => v.lang.startsWith("en"));
        if (preferred) utt.voice = preferred;
        synth.speak(utt);
    };

    useEffect(() => {
        if (!enabled) {
            synthRef.current.cancel();
            return;
        }

        const handler = (e) => {
            const el = document.elementFromPoint(e.clientX, e.clientY);
            const desc = describe(el);
            if (desc) speak(desc);
        };

        document.addEventListener("click", handler, true);
        speak("TalkBack enabled. Click anywhere to hear a description.");

        return () => {
            document.removeEventListener("click", handler, true);
            synthRef.current.cancel();
        };
    }, [enabled]);
};
