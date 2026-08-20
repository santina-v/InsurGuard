import React, { useState } from "react";
import { motion } from "framer-motion";

const DOC_ICONS = {
  police_report: { icon: "🚓", cssClass: "fact-doc-police", label: "Police Report" },
  medical_report: { icon: "🏥", cssClass: "fact-doc-medical", label: "Medical Report" },
  repair_invoice: { icon: "🔧", cssClass: "fact-doc-repair", label: "Repair Invoice" },
};

function ExtractedFacts({ facts }) {
  const [showRaw, setShowRaw] = useState(false);

  if (!facts) return null;

  const renderFactList = (docName, docFacts, index) => {
    const config = DOC_ICONS[docName] || { icon: "📄", cssClass: "", label: docName.replace("_", " ") };

    return (
      <motion.div
        key={docName}
        className={`fact-doc-card ${config.cssClass}`}
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 + index * 0.1 }}
        whileHover={{ borderColor: "var(--border-glow)" }}
      >
        <div className="fact-doc-header">
          <div className="fact-doc-icon">{config.icon}</div>
          <h3 style={{ margin: 0, fontSize: "15px", textTransform: "capitalize" }}>
            {config.label}
          </h3>
        </div>
        <div className="fact-grid">
          {Object.entries(docFacts).map(([key, value]) => (
            <div className="fact-item" key={key}>
              <span className="fact-key">{key.replaceAll("_", " ")}</span>
              <strong className="fact-value">{value === null ? "N/A" : String(value)}</strong>
            </div>
          ))}
        </div>
      </motion.div>
    );
  };

  return (
    <motion.section
      className="facts-panel result-card"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.6 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">AGENT 1</span>
          <h2>Report Summary</h2>
          <p>Structured data parsed from documents</p>
        </div>
        <button className="toggle-btn" onClick={() => setShowRaw(!showRaw)}>
          {showRaw ? "View Structured" : "View Raw JSON"}
        </button>
      </div>

      {showRaw ? (
        <pre style={{
          background: "var(--bg-input)",
          padding: "16px",
          borderRadius: "var(--radius-md)",
          overflowX: "auto",
          fontSize: "12px",
          color: "var(--text-primary)",
          border: "1px solid var(--border-color)",
        }}>
          {JSON.stringify(facts, null, 2)}
        </pre>
      ) : (
        <div className="facts-container">
          {Object.entries(facts).map(([docName, docFacts], index) => renderFactList(docName, docFacts, index))}
        </div>
      )}
    </motion.section>
  );
}

export default ExtractedFacts;
