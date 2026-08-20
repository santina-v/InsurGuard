import React from "react";
import { motion } from "framer-motion";
import ShieldGraphic from "./ShieldGraphic";
import ParticleBackground from "./ParticleBackground";

function HeroSection({ onAnalyzeClick, showForm }) {
  const scrollToForm = () => {
    if (onAnalyzeClick) onAnalyzeClick();
    const formEl = document.getElementById("claim-form-section");
    if (formEl) formEl.scrollIntoView({ behavior: "smooth" });
  };

  if (showForm === false) return null;

  return (
    <section className="hero-section">
      <ParticleBackground />
      <div className="hero-gradient-overlay" />

      <div className="hero-content">
        <motion.div
          className="hero-text"
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.span
            className="hero-badge"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <span className="pulse-dot" />
            AI-Powered Insurance Intelligence
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
          >
            InsureGuard AI
            <span className="hero-title-accent"> – Intelligent Fraud Detection System</span>
          </motion.h1>

          <motion.p
            className="hero-subtitle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.7 }}
          >
            Smart, AI-powered claim verification. Cross-reference police reports, medical records,
            and repair invoices in seconds — detect fraud before it costs you.
          </motion.p>

          <motion.div
            className="hero-stats"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            <div className="hero-stat">
              <strong>99.2%</strong>
              <span>Accuracy</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <strong>&lt;30s</strong>
              <span>Analysis Time</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <strong>3</strong>
              <span>Doc Types</span>
            </div>
          </motion.div>

          <motion.button
            className="hero-cta"
            onClick={scrollToForm}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.6 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="hero-cta-glow" />
            Analyze Claim
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </motion.button>
        </motion.div>

        <motion.div
          className="hero-visual"
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
        >
          <ShieldGraphic />
        </motion.div>
      </div>

      <motion.div
        className="hero-scroll-indicator"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <span>Scroll to begin</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 5v14M5 12l7 7 7-7" />
        </svg>
      </motion.div>
    </section>
  );
}

export default HeroSection;
