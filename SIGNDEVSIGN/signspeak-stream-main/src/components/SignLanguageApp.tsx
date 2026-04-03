import { useEffect, useState, useRef } from "react";
import VideoPanel from "./VideoPanel";
import TypewriterText from "./TypewriterText";

const SignLanguageApp = () => {
  const [outputText, setOutputText] = useState("");
  const inputImgRef = useRef<HTMLImageElement>(null);
  const outputCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // 🔹 Auto-start backend when dashboard loads
    fetch("http://localhost:8001/start").catch(() => {
    console.warn("Backend not reachable");
   });

    // ---------- INPUT (LIVE DETECTION) ----------
    const inputImg = inputImgRef.current;
    if (!inputImg) return;

    const inputSocket = new WebSocket("ws://localhost:8765");
    inputSocket.binaryType = "arraybuffer";

    inputSocket.onmessage = (event) => {
      const blob = new Blob([event.data], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);
      inputImg.src = url;
      setTimeout(() => URL.revokeObjectURL(url), 100);
    };

    inputSocket.onopen = () => {
      console.log("✅ Input WebSocket connected");
    };

    inputSocket.onerror = (e) => {
      console.error("❌ Input WS error", e);
    };

    // ---------- OUTPUT (SIGN PLAYBACK) ----------
    const outputCanvas = outputCanvasRef.current;
    if (!outputCanvas) return;
    const outputCtx = outputCanvas.getContext("2d");

    const outputSocket = new WebSocket("ws://localhost:8766");
    outputSocket.binaryType = "arraybuffer";

    outputSocket.onopen = () => {
      console.log("✅ Output WebSocket connected");
    };

    outputSocket.onmessage = (event) => {
      const blob = new Blob([event.data], { type: "image/jpeg" });
      const img = new Image();

      img.onload = () => {
        if (outputCanvas && outputCtx) {
          outputCanvas.width = img.width;
          outputCanvas.height = img.height;
          outputCtx.drawImage(img, 0, 0);
          URL.revokeObjectURL(img.src);
        }
      };

      img.src = URL.createObjectURL(blob);
    };

    // ---------- TEXT OUTPUT ----------
    const textSocket = new WebSocket("ws://localhost:8767");

    textSocket.onmessage = (event) => {
      setOutputText(event.data);
    };

    textSocket.onopen = () => {
      console.log("✅ Text WebSocket connected");
    };

    // Cleanup
    return () => {
      inputSocket.close();
      outputSocket.close();
      textSocket.close();
    };
  }, []);

  return (
    
    <div
   className="main-fade-in min-h-screen flex flex-col items-center justify-center p-6 lg:p-12 pt-40"
   style={{ backgroundColor: "#020308" }}
    >

      {/* Top-left animated logo/button */}
   <div className="fixed top-6 left-6 z-50">
    <button className="voiceless-btn auto-hover" data-text="VOICELESS">
      <span className="actual-text">&nbsp;VOICELESS&nbsp;</span>
      <span aria-hidden="true" className="hover-text">
        &nbsp;VOICELESS&nbsp;
      </span>
    </button>
   </div>
    

      {/* Main Panels Container */}
      <div className="mt-12 flex flex-col lg:flex-row gap-6 lg:gap-8 w-full max-w-[1400px]">
        {/* Input Panel */}
        <div className="flex-1">
          <VideoPanel label="Live Input" icon="📷">
            <img
              id="input"
              ref={inputImgRef}
              alt="Live webcam input with detection overlay"
              className="w-full aspect-[4/3] object-cover rounded-lg bg-[hsl(var(--card))]"
            />
          </VideoPanel>
        </div>

        {/* Output Panel */}
        <div className="flex-1 flex flex-col">
          <VideoPanel label="Sign Output" icon="🤟">
            <canvas
              id="output"
              ref={outputCanvasRef}
              width={512}
              height={512}
              className="w-full aspect-[4/3] object-contain rounded-lg bg-[hsl(var(--card))]"
            />
          </VideoPanel>

          {/* Text Output */}
          <div id="textOutput">
            <TypewriterText text={outputText} speed={40} />
          </div>
        </div>
      </div>

      {/* Footer hint */}
      <div className="mt-8 text-center">
        <p className="text-muted-foreground text-xs tracking-wider opacity-60">
          
          •"Silence never stopped a voice with purpose"-TheHolyTrinity•
        </p>
      </div>
    </div>
  );
};

export default SignLanguageApp;
