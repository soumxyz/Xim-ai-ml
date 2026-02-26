import React, { useCallback, useEffect, useRef, useState } from "react";

const FlipWords = ({ words, duration = 3000, className = "" }) => {
    const [currentWord, setCurrentWord] = useState(words[0]);
    const [isAnimating, setIsAnimating] = useState(false);
    const indexRef = useRef(0);

    const startAnimation = useCallback(() => {
        indexRef.current = (indexRef.current + 1) % words.length;
        setCurrentWord(words[indexRef.current]);
        setIsAnimating(true);
    }, [words]);

    useEffect(() => {
        const timer = setInterval(() => {
            startAnimation();
        }, duration);
        return () => clearInterval(timer);
    }, [startAnimation, duration]);

    return (
        <span className={`inline-block ${className}`}>
            {currentWord.split("").map((char, i) => (
                <span
                    key={`${currentWord}-${i}`}
                    style={{
                        display: "inline-block",
                        animation: isAnimating
                            ? `flipIn 0.5s ease forwards ${i * 0.04}s`
                            : "none",
                        opacity: isAnimating ? 0 : 1,
                    }}
                    onAnimationEnd={() => {
                        if (i === currentWord.length - 1) setIsAnimating(false);
                    }}
                >
                    {char === " " ? "\u00A0" : char}
                </span>
            ))}
            <style>{`
        @keyframes flipIn {
          0%   { opacity: 0; transform: translateY(10px) rotateX(-90deg); }
          60%  { opacity: 1; transform: translateY(-4px) rotateX(10deg); }
          100% { opacity: 1; transform: translateY(0px) rotateX(0deg); }
        }
      `}</style>
        </span>
    );
};

export { FlipWords };
