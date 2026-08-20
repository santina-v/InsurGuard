import React, { useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

function ShieldGraphic() {
  const ref = useRef(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [12, -12]), { stiffness: 150, damping: 20 });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-12, 12]), { stiffness: 150, damping: 20 });

  const handleMouseMove = (e) => {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    mouseX.set((e.clientX - rect.left) / rect.width - 0.5);
    mouseY.set((e.clientY - rect.top) / rect.height - 0.5);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <div
      ref={ref}
      className="shield-container"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        className="shield-wrapper"
        style={{ rotateX, rotateY, transformPerspective: 800 }}
      >
        <motion.div
          className="shield-glow-ring"
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />
        <motion.div
          className="shield-glow-ring shield-glow-ring-2"
          animate={{ rotate: -360 }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        />

        <svg viewBox="0 0 200 240" className="shield-svg" aria-hidden="true">
          <defs>
            <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.5" />
            </linearGradient>
            <filter id="shieldGlow">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <motion.path
            d="M100 10 L180 50 L180 130 C180 180 140 220 100 230 C60 220 20 180 20 130 L20 50 Z"
            fill="url(#shieldGrad)"
            stroke="#06b6d4"
            strokeWidth="2"
            filter="url(#shieldGlow)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
          <motion.path
            d="M100 40 L155 70 L155 125 C155 160 130 185 100 192 C70 185 45 160 45 125 L45 70 Z"
            fill="none"
            stroke="rgba(255,255,255,0.2)"
            strokeWidth="1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          />
          <motion.text
            x="100"
            y="115"
            textAnchor="middle"
            fill="#fff"
            fontSize="14"
            fontWeight="700"
            fontFamily="Inter, sans-serif"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 0.5 }}
          >
            AI
          </motion.text>
          <motion.path
            d="M85 130 L95 145 L115 120"
            fill="none"
            stroke="#34d399"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 1.5, duration: 0.6 }}
          />
        </svg>

        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="shield-orb"
            style={{
              top: `${20 + (i % 3) * 30}%`,
              left: `${10 + Math.floor(i / 3) * 80}%`,
            }}
            animate={{
              y: [0, -8, 0],
              opacity: [0.3, 0.7, 0.3],
            }}
            transition={{
              duration: 2 + i * 0.3,
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </motion.div>
    </div>
  );
}

export default ShieldGraphic;
