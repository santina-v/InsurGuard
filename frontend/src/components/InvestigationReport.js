import React from "react";
import { motion } from "framer-motion";

function InvestigationReport({ report }) {
  if (!report) return null;

  return (
    <motion.section
      className="report-panel result-card"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.7 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">AGENT 4</span>
          <h2>Investigation Report</h2>
          <p>Explainable assessment for claim investigators</p>
        </div>
      </div>

      <motion.div
        className="report-summary-card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <span style={{ fontSize: "14px", fontWeight: 500, color: "var(--text-secondary)" }}>Final Assessment</span>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span className={`risk-badge risk-${report.risk_level}`}>{report.risk_level}</span>
            <span style={{ fontSize: "14px", fontWeight: 600 }}>{report.risk_percentage}% risk</span>
          </div>
        </div>
        <p style={{ margin: 0, fontSize: "15px", color: "var(--text-primary)", lineHeight: 1.7 }}>
          {report.summary}
        </p>
      </motion.div>

      {report.key_findings?.length > 0 && (
        <div className="report-section">
          <h3 style={{ fontSize: "15px", marginBottom: "12px", color: "var(--text-primary)" }}>Key Findings</h3>
          <div className="report-list">
            {report.key_findings.map((finding, index) => (
              <motion.div
                className="report-list-item"
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.9 + index * 0.08 }}
              >
                <span style={{ color: "var(--color-accent)" }}>▸</span>
                <p style={{ margin: 0, fontSize: "14px" }}>{finding}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {report.recommendations?.length > 0 && (
        <div className="report-section" style={{ marginTop: "24px" }}>
          <h3 style={{ fontSize: "15px", marginBottom: "12px", color: "var(--text-primary)" }}>Recommendations</h3>
          <div className="report-list">
            {report.recommendations.map((rec, index) => (
              <motion.div
                className="report-list-item"
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.0 + index * 0.08 }}
              >
                <span style={{ color: "var(--color-purple)" }}>▸</span>
                <p style={{ margin: 0, fontSize: "14px" }}>{rec}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.section>
  );
}

export default InvestigationReport;
