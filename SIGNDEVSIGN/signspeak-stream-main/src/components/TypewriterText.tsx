import { useEffect, useState, useRef } from "react";

interface TypewriterTextProps {
  text: string;
  speed?: number;
}

const TypewriterText = ({ text, speed = 50 }: TypewriterTextProps) => {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const previousTextRef = useRef("");

  useEffect(() => {
    // If text changed, start typing animation
    if (text !== previousTextRef.current) {
      previousTextRef.current = text;
      setIsTyping(true);
      setDisplayedText("");

      let currentIndex = 0;
      const intervalId = setInterval(() => {
        if (currentIndex < text.length) {
          setDisplayedText(text.slice(0, currentIndex + 1));
          currentIndex++;
        } else {
          setIsTyping(false);
          clearInterval(intervalId);
        }
      }, speed);

      return () => clearInterval(intervalId);
    }
  }, [text, speed]);

  return (
    <div className="glass-panel p-4 mt-4 min-h-[60px] flex items-center">
      <p className="typewriter-text flex-1">
        {displayedText || <span className="text-muted-foreground italic">Waiting for output...</span>}
      </p>
      <span className={`typewriter-cursor ${!isTyping && displayedText ? "opacity-100" : ""}`} />
    </div>
  );
};

export default TypewriterText;
