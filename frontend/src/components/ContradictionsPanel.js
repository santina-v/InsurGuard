import React from "react";
import { motion } from "framer-motion";

function ContradictionsPanel({ contradictions }) {
  if (!contradictions || contradictions.length === 0) {
    return (
      <motion.section
        className="result-card contradictions-panel"
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <div className="panel-heading">
          <div>
            <span className="section-eyebrow">ANOMALY DETECTION</span>
            <h2>Contradictions</h2>
            <p>Cross-document consistency analysis</p>
          </div>
        </div>
        <motion.div
          className="no-contradictions-banner"
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.6 }}
        >
          ✓ No contradictions found across the claim documents.
        </motion.div>
      </motion.section>
    );
  }

  return (
    <motion.section
      className="result-card contradictions-panel"
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">ANOMALY DETECTION</span>
          <h2>Contradictions Detected</h2>
          <p>{contradictions.length} inconsistenc{contradictions.length === 1 ? "y" : "ies"} found.</p>
        </div>
      </div>

      <div className="contradictions-list">
        {contradictions.map((item, index) => (
          <motion.div
            className={`contradiction-card contradiction-${item.severity?.toLowerCase() || "medium"}`}
            key={index}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 + index * 0.1 }}
            whileHover={{ x: 4 }}
          >
            <div className="contradiction-top">
              <h3>{item.type?.replaceAll("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}</h3>
              <span
                className="severity-badge"
                style={{
                  color: item.severity?.toLowerCase() === "high" ? "var(--color-mismatch-text)" :
                    item.severity?.toLowerCase() === "medium" ? "var(--color-unknown-text)" : "var(--color-match-text)",
                }}
              >
                {item.severity?.toUpperCase()} SEVERITY
              </span>
            </div>

            <p style={{ margin: "0 0 16px 0", fontSize: "14px", color: "var(--text-primary)" }}>
              {item.description || item.explanation}
            </p>

            {item.evidence && item.evidence.length > 0 && (
              <div className="evidence">
                <strong style={{ fontSize: "12px", color: "var(--text-secondary)", textTransform: "uppercase" }}>Conflicting Evidence</strong>
                {item.evidence.map((ev, i) => (
                  <div className="evidence-item" key={i}>
                    <span>{ev.source}:</span> {ev.fact}
                  </div>
                ))}
              </div>
            )}

            {(!item.evidence || item.evidence.length === 0) && item.sources && item.sources.length > 0 && (
              <div className="evidence" style={{ fontSize: "13px" }}>
                <span style={{ fontWeight: 600 }}>Sources:</span> {item.sources.join(", ")}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}

export default ContradictionsPanel;
