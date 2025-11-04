import React from "react";

export default function SoundToggle() {
  const ref = React.useRef(null);
  const [on, setOn] = React.useState(false);
  const [available, setAvailable] = React.useState(true);

  React.useEffect(() => {
    const audio = ref.current;
    if (!audio) {
      return;
    }
    audio.volume = 0.3;
    if (on) {
      audio.play().catch(() => setOn(false));
    } else {
      audio.pause();
    }
    return () => {
      audio.pause();
    };
  }, [on]);

  if (!available) {
    return null;
  }

  return (
    <div style={{ position: "fixed", right: 18, bottom: 18, zIndex: 6 }}>
      <audio
        ref={ref}
        loop
        src="/assets/audio/ambience.mp3"
        onError={() => setAvailable(false)}
      />
      <button
        type="button"
        onClick={() => setOn((v) => !v)}
        style={{
          background: "rgba(0,0,0,.35)",
          color: "#7affcf",
          border: "1px solid rgba(0,255,160,.25)",
          borderRadius: 12,
          padding: "10px 14px",
          cursor: "pointer",
          boxShadow: "0 0 12px rgba(0,255,160,.25)",
        }}
      >
        {on ? "🔊 Ambiance" : "🔈 Ambiance"}
      </button>
    </div>
  );
}
