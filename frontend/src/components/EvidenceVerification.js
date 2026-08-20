import React from "react";
import { motion } from "framer-motion";

function EvidenceVerification({ verification }) {
  if (!verification) return null;

  const getVerificationClass = (status) => {
    if (status === "MATCH") return "verification-match";
    if (status === "MISMATCH") return "verification-mismatch";
    return "verification-unknown";
  };

  const getVerificationIcon = (status) => {
    if (status === "MATCH") return "✓";
    if (status === "MISMATCH") return "!";
    return "?";
  };

  const checks = [
    ["Identity", verification.identity, "👤"],
    ["Vehicle", verification.vehicle, "🚗"],
    ["Date", verification.date, "📅"],
    ["Timeline", verification.timeline, "⏱️"],
    ["Damage", verification.damage, "💥"],
  ];

  return (
    <motion.section
      className="verification-panel result-card"
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">AGENT 2</span>
          <h2>Evidence Verification</h2>
          <p>Cross-document consistency analysis</p>
        </div>
        <span className={`risk-badge ${getVerificationClass(verification.overall_status)}`}>
          {verification.overall_status}
        </span>
      </div>

      <div className="verification-grid">
        {checks.map(([label, status, emoji], index) => (
          <motion.div
            className="verification-item"
            key={label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 + index * 0.08 }}
            whileHover={{ y: -2 }}
          >
            <div className={`verification-icon ${getVerificationClass(status)}`}>
              {getVerificationIcon(status)}
            </div>
            <div>
              <strong>{emoji} {label}</strong>
              <span className={getVerificationClass(status)} style={{ display: "block", fontSize: "12px", fontWeight: 600 }}>
                {status}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {verification.evidence?.length > 0 && (
        <div className="verification-evidence">
          <h3 style={{ fontSize: "15px", marginBottom: "12px" }}>Verification Details</h3>
          {verification.evidence.map((item, index) => (
            <motion.div
              className="verification-evidence-item"
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 + index * 0.05 }}
              style={{
                borderLeftColor: item.status === "MATCH" ? "var(--color-match)" : item.status === "MISMATCH" ? "var(--color-mismatch)" : "var(--color-unknown)",
              }}
            >
              <div>
                <strong>{item.type?.replaceAll("_", " ")}</strong>
                <span className={getVerificationClass(item.status)} style={{ fontSize: "11px", fontWeight: 700 }}>
                  {item.status}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "13px" }}>{item.description}</p>
            </motion.div>
          ))}
        </div>
      )}
    </motion.section>
  );
}

export default EvidenceVerification;
