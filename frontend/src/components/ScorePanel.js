import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

function ScorePanel({ result }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  const getRiskPercentage = () => {
    if (result?.risk_percentage !== undefined && result?.risk_percentage !== null) return Number(result.risk_percentage);
    if (result?.risk_score !== undefined && result?.risk_score !== null) return Number(result.risk_score) * 100;
    if (result?.reasoning?.risk_percentage !== undefined && result?.reasoning?.risk_percentage !== null) return Number(result.reasoning.risk_percentage);
    if (result?.reasoning?.risk_score !== undefined && result?.reasoning?.risk_score !== null) return Number(result.reasoning.risk_score) * 100;
    return 0;
  };

  const riskPercentage = Math.max(0, Math.min(100, Math.round(getRiskPercentage())));
  const riskLevel = String(result?.risk_level || result?.reasoning?.risk_level || (riskPercentage >= 70 ? "HIGH" : riskPercentage >= 40 ? "MEDIUM" : "LOW")).toUpperCase();
  const contributors = Array.isArray(result?.score_contributors) ? result.score_contributors : [];

  useEffect(() => {
    const duration = 1500;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(eased * riskPercentage));
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [riskPercentage]);

  const formatFeatureName = (feature) => {
    if (!feature) return "Risk Factor";
    return String(feature).replaceAll("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const getContributorPercentage = (weight) => {
    const numericWeight = Number(weight);
    if (!Number.isFinite(numericWeight)) return 0;
    const percentage = numericWeight <= 1 ? numericWeight * 100 : numericWeight;
    return Math.max(0, Math.min(100, Math.round(percentage)));
  };

  const getRiskColor = () => {
    if (riskLevel === "HIGH") return "var(--color-high-risk)";
    if (riskLevel === "MEDIUM") return "var(--color-medium-risk)";
    return "var(--color-low-risk)";
  };

  const circumference = 2 * Math.PI * 85;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  return (
    <motion.section
      className="score-panel result-card"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">FINAL ASSESSMENT</span>
          <h2>AI Fraud Score</h2>
          <p>AI-powered claim risk assessment</p>
        </div>
        <motion.span
          className={`risk-badge risk-${riskLevel}`}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.8, type: "spring" }}
        >
          {riskLevel} RISK
        </motion.span>
      </div>

      <div className="score-dashboard-grid">
        <div className="score-ring-container">
          <svg className="score-ring-svg" width="200" height="200" viewBox="0 0 200 200">
            <circle className="score-ring-bg" cx="100" cy="100" r="85" />
            <motion.circle
              className="score-ring-fill"
              cx="100"
              cy="100"
              r="85"
              stroke={getRiskColor()}
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />
          </svg>
          <div className="score-ring-center">
            <div className={`score-number risk-${riskLevel}`}>{animatedScore}%</div>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Fraud Risk</span>
          </div>
        </div>

        <div className="score-contributors">
          <h3>Score Contributors</h3>
          {contributors.length === 0 ? (
            <div style={{ padding: "12px", background: "var(--bg-glass)", borderRadius: "var(--radius-md)", fontSize: "13px", color: "var(--text-muted)" }}>
              No specific score contributors detected.
            </div>
          ) : (
            <div style={{ display: "grid", gap: "12px", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))" }}>
              {contributors.map((contributor, index) => {
                const percentage = getContributorPercentage(contributor?.weight);
                return (
                  <motion.div
                    className="contributor"
                    key={`${contributor?.feature || "risk"}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                  >
                    <div className="contributor-header">
                      <strong style={{ color: "var(--text-primary)" }}>{formatFeatureName(contributor?.feature)}</strong>
                      <span style={{ color: "var(--color-accent)" }}>{percentage}%</span>
                    </div>
                    <p>{contributor?.description || "This factor contributed to the overall risk score."}</p>
                    <div className="contributor-bar">
                      <motion.div
                        className="contributor-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 1, delay: 0.6 + index * 0.1 }}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </motion.section>
  );
}

export default ScorePanel;
