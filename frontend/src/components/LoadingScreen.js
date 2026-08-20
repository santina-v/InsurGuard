import React from "react";
import { motion, AnimatePresence } from "framer-motion";

function LoadingScreen({ steps, loadingStep }) {
  return (
    <motion.div
      className="loading-screen glass-card"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.4 }}
    >
      <div className="loading-shield-spinner">
        <motion.div
          className="loading-ring"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />
        <motion.div
          className="loading-ring loading-ring-inner"
          animate={{ rotate: -360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        />
        <span className="loading-shield-icon">🛡️</span>
      </div>

      <motion.h2
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        Analyzing Claim Data
      </motion.h2>
      <motion.p
        className="loading-subtitle"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        Our AI agents are cross-referencing documents...
      </motion.p>

      <div className="loading-steps-container">
        <AnimatePresence mode="sync">
          {steps.map((step, index) => {
            const isActive = index === loadingStep;
            const isDone = index < loadingStep;
            return (
              <motion.div
                key={step}
                className={`loading-step-item ${isActive ? "active" : ""} ${isDone ? "done" : ""}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.08 }}
              >
                <div className="loading-step-indicator">
                  {isDone ? (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="step-check"
                    >
                      ✓
                    </motion.span>
                  ) : isActive ? (
                    <motion.span
                      className="step-spinner"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                  ) : (
                    <span className="step-pending" />
                  )}
                </div>
                <span className="loading-step-label">{step}</span>
                {isActive && (
                  <motion.div
                    className="loading-step-progress"
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 1 }}
                  />
                )}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      <div className="loading-agents">
        {["Agent 1: Extraction", "Agent 2: Verification", "Agent 3: Graph", "Agent 4: Report"].map((agent, i) => (
          <motion.span
            key={agent}
            className="loading-agent-badge"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
          >
            {agent}
          </motion.span>
        ))}
      </div>
    </motion.div>
  );
}

export default LoadingScreen;
