import React, { useState } from "react";
import { motion } from "framer-motion";

const DOC_CONFIG = {
  police_report: {
    title: "Police Report",
    icon: "🚓",
    desc: "Incident details, reported circumstances and official account.",
    cssClass: "doc-police",
    badge: "Official Record",
    stamp: "FIR",
  },
  medical_report: {
    title: "Medical Report",
    icon: "🏥",
    desc: "Patient assessment, treatment timeline and injury details.",
    cssClass: "doc-medical",
    badge: "Clinical Doc",
    stamp: "Rx",
  },
  repair_invoice: {
    title: "Repair Invoice",
    icon: "🔧",
    desc: "Vehicle damage assessment and estimated repair costs.",
    cssClass: "doc-repair",
    badge: "Cost Breakdown",
    stamp: "INV",
  },
};

function ClaimInputForm({ onAnalyze, loading }) {
  const [files, setFiles] = useState({
    police_report: null,
    medical_report: null,
    repair_invoice: null,
  });

  const [formData, setFormData] = useState({
    claim_amount: "",
    region_avg_claim_amount: "",
    claimant_prior_claims_18mo: "",
    policy_tenure_months: "",
    location_lat: "",
    location_lon: "",
  });

  const [step, setStep] = useState(1);

  const acceptedFormats = ".pdf,.docx,.doc,.jpg,.jpeg,.png,.txt,.xlsx,.xls,.csv";

  const handleFileChange = (e, docType) => {
    const file = e.target.files?.[0];
    if (file) {
      setFiles((prev) => ({ ...prev, [docType]: file }));
    }
  };

  const handleRemoveFile = (docType) => {
    setFiles((prev) => ({ ...prev, [docType]: null }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleReview = (e) => {
    e.preventDefault();
    if (!files.police_report) return alert("Police Report is required.");
    if (!files.medical_report) return alert("Medical Report is required.");
    if (!files.repair_invoice) return alert("Repair Invoice is required.");
    setStep(2);
  };

  const handleSubmit = () => {
    onAnalyze({
      police_report: files.police_report,
      medical_report: files.medical_report,
      repair_invoice: files.repair_invoice,
      claim_amount: Number(formData.claim_amount),
      region_avg_claim_amount: Number(formData.region_avg_claim_amount),
      claimant_prior_claims_18mo: Number(formData.claimant_prior_claims_18mo),
      policy_tenure_months: Number(formData.policy_tenure_months),
      location_lat: formData.location_lat ? Number(formData.location_lat) : null,
      location_lon: formData.location_lon ? Number(formData.location_lon) : null,
    });
  };

  const DocumentUploadCard = ({ docType }) => {
    const config = DOC_CONFIG[docType];
    const file = files[docType];

    return (
      <motion.div
        className={`document-upload-card ${config.cssClass} ${file ? "has-file" : ""}`}
        whileHover={{ y: -4 }}
        transition={{ duration: 0.3 }}
      >
        <span className="doc-type-badge">{config.badge}</span>
        <div className="upload-icon-wrapper">{config.icon}</div>
        <h3 style={{ margin: "0 0 8px 0", fontSize: "16px", fontWeight: 600 }}>{config.title}</h3>
        {!file ? (
          <>
            <p style={{ margin: "0 0 16px 0", fontSize: "13px", color: "var(--text-secondary)" }}>{config.desc}</p>
            <label className="upload-button">
              Upload Document
              <input type="file" accept={acceptedFormats} onChange={(e) => handleFileChange(e, docType)} hidden />
            </label>
            <div style={{ marginTop: "12px", fontSize: "11px", color: "var(--text-muted)" }}>
              Supported: PDF, DOCX, JPG, PNG, TXT, CSV, XLS
            </div>
          </>
        ) : (
          <div className="selected-file">
            <span>✓</span>
            <div style={{ flex: 1 }}>
              <strong>{file.name}</strong>
              <small>{(file.size / 1024).toFixed(1)} KB • {file.type || "Unknown Type"}</small>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <label className="upload-button" style={{ marginTop: 0, padding: "4px 8px", fontSize: "11px" }}>
                Replace
                <input type="file" accept={acceptedFormats} onChange={(e) => handleFileChange(e, docType)} hidden />
              </label>
              <button type="button" className="remove-btn" onClick={() => handleRemoveFile(docType)}>Remove</button>
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  if (step === 2) {
    return (
      <motion.div
        className="claim-form glass-card"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="panel-heading">
          <div>
            <span className="section-eyebrow">STEP 2 OF 2</span>
            <h2>Review Claim Data</h2>
            <p>Verify the information before starting the analysis.</p>
          </div>
          <button type="button" className="upload-button" onClick={() => setStep(1)} style={{ marginTop: 0 }}>Back to Edit</button>
        </div>

        <div className="review-grid">
          <motion.div className="result-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <h3>Documents to Analyze</h3>
            <ul className="review-doc-list">
              {Object.entries(DOC_CONFIG).map(([key, config]) => (
                <li key={key}>
                  <span>{config.icon}</span>
                  <strong>{config.title}:</strong> {files[key]?.name}
                </li>
              ))}
            </ul>
          </motion.div>
          <motion.div className="result-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <h3>Claim Context</h3>
            <ul className="review-doc-list">
              <li><strong>Amount:</strong> ${formData.claim_amount}</li>
              <li><strong>Regional Avg:</strong> ${formData.region_avg_claim_amount}</li>
              <li><strong>Prior Claims (18mo):</strong> {formData.claimant_prior_claims_18mo}</li>
              <li><strong>Policy Tenure:</strong> {formData.policy_tenure_months} months</li>
              {formData.location_lat && <li><strong>Location:</strong> {formData.location_lat}, {formData.location_lon}</li>}
            </ul>
          </motion.div>
        </div>

        <motion.button
          type="button"
          className="analyze-button"
          onClick={handleSubmit}
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? "Analyzing..." : "Analyze Claim"}
        </motion.button>
      </motion.div>
    );
  }

  return (
    <motion.form
      className="claim-form glass-card"
      onSubmit={handleReview}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">STEP 1 OF 2</span>
          <h2>Document Intake</h2>
          <p>Upload the required documentation to begin the investigation.</p>
        </div>
      </div>

      <div className="documents-grid">
        {Object.keys(DOC_CONFIG).map((docType, i) => (
          <motion.div
            key={docType}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <DocumentUploadCard docType={docType} />
          </motion.div>
        ))}
      </div>

      <div className="panel-heading" style={{ marginTop: "24px" }}>
        <div>
          <h2>Claim Context</h2>
          <p>Contextual data for risk scoring.</p>
        </div>
      </div>

      <div className="metadata-grid">
        <div className="input-group">
          <label>Claim Amount ($)</label>
          <input type="number" name="claim_amount" value={formData.claim_amount} onChange={handleChange} required min="0" />
        </div>
        <div className="input-group">
          <label>Regional Avg Claim ($)</label>
          <input type="number" name="region_avg_claim_amount" value={formData.region_avg_claim_amount} onChange={handleChange} required min="0" />
        </div>
        <div className="input-group">
          <label>Prior Claims (18mo)</label>
          <input type="number" name="claimant_prior_claims_18mo" value={formData.claimant_prior_claims_18mo} onChange={handleChange} required min="0" />
        </div>
        <div className="input-group">
          <label>Policy Tenure (months)</label>
          <input type="number" name="policy_tenure_months" value={formData.policy_tenure_months} onChange={handleChange} required min="0" />
        </div>
      </div>

      <div className="panel-heading" style={{ marginTop: "24px" }}>
        <div>
          <h2>Incident Location <span style={{ color: "var(--text-muted)", fontWeight: 400, fontSize: 14 }}>(Optional)</span></h2>
        </div>
      </div>

      <div className="metadata-grid">
        <div className="input-group">
          <label>Latitude</label>
          <input type="number" step="any" name="location_lat" value={formData.location_lat} onChange={handleChange} placeholder="e.g. 12.9716" />
        </div>
        <div className="input-group">
          <label>Longitude</label>
          <input type="number" step="any" name="location_lon" value={formData.location_lon} onChange={handleChange} placeholder="e.g. 77.5946" />
        </div>
      </div>

      <motion.button
        type="submit"
        className="analyze-button"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        Review Claim
      </motion.button>
    </motion.form>
  );
}

export default ClaimInputForm;
