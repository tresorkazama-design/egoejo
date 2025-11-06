// src/cursor.jsx
import React, { useEffect, useRef } from "react";
import "./cursor.css";

export default function CustomCursor() {
  const dotRef = useRef(null);
  const ringRef = useRef(null);
  const trailRef = useRef(null);

  useEffect(() => {
    const dot = dotRef.current;
    const ring = ringRef.current;
    const trail = trailRef.current;

    let x = window.innerWidth / 2;
    let y = window.innerHeight / 2;
    let rx = x, ry = y;
    let down = false;
    const lerp = (a, b, t) => a + (b - a) * t;

    const onMove = (e) => {
      x = e.clientX;
      y = e.clientY;
    };
    const onDown = () => (down = true);
    const onUp = () => (down = false);
    const onEnter = () => {
      dot.style.opacity = "1";
      ring.style.opacity = "1";
    };
    const onLeave = () => {
      dot.style.opacity = "0";
      ring.style.opacity = "0";
    };

    // petite traînée
    const bubbles = [];
    const spawnBubble = (bx, by) => {
      const s = document.createElement("span");
      s.style.left = bx + "px";
      s.style.top = by + "px";
      trail.appendChild(s);
      setTimeout(() => trail.removeChild(s), 300);
      bubbles.push(s);
      if (bubbles.length > 12) {
        const rm = bubbles.shift();
        rm && rm.remove();
      }
    };

    const raf = () => {
      rx = lerp(rx, x, 0.2);
      ry = lerp(ry, y, 0.2);

      dot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${down ? 0.8 : 1})`;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%) scale(${down ? 0.9 : 1})`;

      if (Math.random() < 0.5) spawnBubble(rx, ry);
      requestAnimationFrame(raf);
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup", onUp);
    window.addEventListener("mouseenter", onEnter);
    window.addEventListener("mouseleave", onLeave);

    requestAnimationFrame(raf);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("mouseup", onUp);
      window.removeEventListener("mouseenter", onEnter);
      window.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  return (
    <>
      <div ref={trailRef} className="cursor-trail" />
      <div ref={ringRef} className="cursor-outline" />
      <div ref={dotRef} className="cursor-dot" />
    </>
  );
}
