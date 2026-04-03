import { useEffect, useState } from "react";

type LoaderProps = {
  onFinish: () => void;
  duration?: number;
};

export default function LoadingScreen({
  onFinish,
  duration = 7000,
}: LoaderProps) {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setFadeOut(true);
      setTimeout(onFinish, 700); // wait for fade animation
    }, duration);

    return () => clearTimeout(timer);
  }, [onFinish, duration]);

  return (
    <div
      className={`fixed inset-0 z-50 bg-black transition-all duration-700
      ${fadeOut ? "opacity-0 blur-xl" : "opacity-100 blur-0"}`}
    >
      <video
        src="/loader.mp4"
        autoPlay
        muted
        playsInline
        className="w-full h-full object-cover"
      />
    </div>
  );
}
