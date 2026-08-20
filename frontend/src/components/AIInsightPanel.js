import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

function TypewriterText({ text, delay = 0, speed = 30 }) {
  const [displayed, setDisplayed] = useState("");
  const [started, setStarted] = useState(false);

  useEffect(() => {
    const startTimer = setTimeout(() => setStarted(true), delay);
    return () => clearTimeout(startTimer);
  }, [delay]);

  useEffect(() => {
    if (!started) return;
    let i = 0;
    const interval = setInterval(() => {
      if (i <= text.length) {
        setDisplayed(text.slice(0, i));
        i++;
      } else {
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, started, speed]);

  return <span>{displayed}<span className="typing-cursor">|</span></span>;
}

function AIInsightPanel({ result }) {
  if (!result) return null;

  const riskLevel = String(result?.risk_level || "MEDIUM").toUpperCase();
  const riskPercentage = Math.round(Number(result?.risk_percentage) || 0);
  const contradictionCount = Array.isArray(result?.contradictions) ? result.contradictions.length : 0;
  const confidenceScore = Math.max(60, Math.min(98, 100 - Math.round(riskPercentage * 0.3) + (contradictionCount > 0 ? -5 : 10)));

  const insights = [
    {
      label: "AI Confidence Score",
      value: `${confidenceScore}%`,
      icon: "🎯",
      color: "cyan",
      delay: 0,
    },
    {
      label: "Fraud Risk",
      value: riskLevel,
      icon: riskLevel === "HIGH" ? "🔴" : riskLevel === "MEDIUM" ? "🟡" : "🟢",
      color: riskLevel === "HIGH" ? "red" : riskLevel === "MEDIUM" ? "yellow" : "green",
      delay: 400,
    },
    {
      label: "Detected Anomalies",
      value: String(contradictionCount),
      icon: "⚠️",
      color: contradictionCount > 0 ? "yellow" : "green",
      delay: 800,
    },
    {
      label: "Documents Verified",
      value: result?.verification?.overall_status || "PENDING",
      icon: result?.verification?.overall_status === "MATCH" ? "✅" : "🔍",
      color: "cyan",
      delay: 1200,
    },
  ];

  return (
    <motion.section
      className="ai-insight-panel glass-card"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
    >
      <div className="ai-panel-header">
        <div className="ai-avatar">
          <motion.div
            className="ai-avatar-pulse"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span>🤖</span>
        </div>
        <div>
          <span className="section-eyebrow">AI ANALYSIS ENGINE</span>
          <h2>Intelligence Insights</h2>
          <p className="ai-typing-line">
            <TypewriterText
              text={`Analysis complete. ${contradictionCount} anomal${contradictionCount === 1 ? "y" : "ies"} detected across claim documents.`}
              delay={500}
              speed={25}
            />
          </p>
        </div>
      </div>

      <div className="ai-insights-grid">
        {insights.map((insight, index) => (
          <motion.div
            key={insight.label}
            className={`ai-insight-card ai-insight-${insight.color}`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + index * 0.15, duration: 0.4 }}
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <span className="ai-insight-icon">{insight.icon}</span>
            <div>
              <span className="ai-insight-label">{insight.label}</span>
              <motion.strong
                className="ai-insight-value"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: insight.delay / 1000 + 0.5 }}
              >
                {insight.value}
              </motion.strong>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}

export default AIInsightPanel;
