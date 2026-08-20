import React, { useState, useEffect } from "react";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import "./App.css";

import HeroSection from "./components/HeroSection";
import ThemeToggle from "./components/ThemeToggle";
import LoadingScreen from "./components/LoadingScreen";
import AIInsightPanel from "./components/AIInsightPanel";
import ClaimInputForm from "./components/ClaimInputForm";
import ScorePanel from "./components/ScorePanel";
import GraphPanel from "./components/GraphPanel";
import ContradictionsPanel from "./components/ContradictionsPanel";
import EvidenceVerification from "./components/EvidenceVerification";
import InvestigationReport from "./components/InvestigationReport";
import ExtractedFacts from "./components/ExtractedFacts";

function AIAssistant() {
  const [open, setOpen] = useState(false);

  return (
    <div className="ai-assistant-popup">
      <AnimatePresence>
        {open && (
          <motion.div
            className="ai-assistant-chat"
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
          >
            <div className="ai-chat-header">
              <span>🤖</span>
              <div>
                <strong style={{ fontSize: 14 }}>InsureGuard Assistant</strong>
                <p style={{ margin: 0, fontSize: 11, color: "var(--text-muted)" }}>Always online</p>
              </div>
            </div>
            <div className="ai-chat-message">
              Hi! I can help you analyze insurance claims. Upload your police report, medical records, and repair invoice to get started with AI-powered fraud detection.
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <motion.button
        className="ai-assistant-btn"
        onClick={() => setOpen(!open)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        aria-label="AI Assistant"
      >
        💬
      </motion.button>
    </div>
  );
}

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState("dark");

  const steps = [
    "Document Ingestion",
    "Fact Extraction",
    "Evidence Verification",
    "Contradiction Analysis",
    "Knowledge Graph Construction",
    "Fraud Reasoning",
    "Report Generation",
  ];

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loading, steps.length]);

  const analyzeClaim = async (claimData) => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("police_report", claimData.police_report);
      formData.append("medical_report", claimData.medical_report);
      formData.append("repair_invoice", claimData.repair_invoice);
      formData.append("claim_amount", String(Number(claimData.claim_amount)));
      formData.append("region_avg_claim_amount", String(Number(claimData.region_avg_claim_amount)));
      formData.append("claimant_prior_claims_18mo", String(Number(claimData.claimant_prior_claims_18mo)));
      formData.append("policy_tenure_months", String(Number(claimData.policy_tenure_months)));

      if (claimData.location_lat) formData.append("location_lat", String(Number(claimData.location_lat)));
      if (claimData.location_lon) formData.append("location_lon", String(Number(claimData.location_lon)));

      const response = await axios.post("http://localhost:8000/api/claims/analyze-pdfs", formData);
      setResult(response.data);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      if (err.response) {
        const detail = err.response.data?.detail;
        if (Array.isArray(detail)) {
          setError(detail.map((item) => `${item.loc?.[item.loc.length - 1] || "field"}: ${item.msg}`).join(" | "));
        } else {
          setError(detail || `Backend error: ${err.response.status}`);
        }
      } else if (err.request) {
        setError("Cannot connect to backend. Make sure FastAPI is running on port 8000.");
      } else {
        setError(err.message || "Something went wrong while analyzing the claim.");
      }
    } finally {
      setLoading(false);
    }
  };

  const showHero = !result && !loading;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-brand">
            <div className="header-logo">🛡️</div>
            <div>
              <h1>InsurGuard AI</h1>
              <p>Intelligent Fraud Detection</p>
            </div>
          </div>
          <div className="header-actions">
            <span className="header-status">
              <span className="pulse-dot" />
              System Online
            </span>
            <ThemeToggle theme={theme} onToggle={() => setTheme(theme === "dark" ? "light" : "dark")} />
          </div>
        </div>
      </header>

      {showHero && <HeroSection showForm={!result} />}

      <main className="container">
        <div id="claim-form-section">
          {!result && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <ClaimInputForm onAnalyze={analyzeClaim} loading={loading} />
            </motion.div>
          )}
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              className="error-box"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <h3>Analysis failed</h3>
              <p>{error}</p>
              <button className="analyze-button btn-secondary" style={{ width: "auto", padding: "10px 24px", marginTop: 12 }} onClick={() => setError("")}>
                Try Again
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {loading && <LoadingScreen steps={steps} loadingStep={loadingStep} />}
        </AnimatePresence>

        <AnimatePresence>
          {result && !loading && (
            <motion.div
              className="results-command-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="results-header">
                <h2>Investigation Results</h2>
                <motion.button
                  className="analyze-button btn-secondary"
                  style={{ width: "auto", padding: "10px 24px" }}
                  onClick={() => setResult(null)}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                >
                  New Investigation
                </motion.button>
              </div>

              <AIInsightPanel result={result} />
              <ScorePanel result={result} />

              <div className="results-grid-2">
                <EvidenceVerification verification={result.verification} />
                <ContradictionsPanel contradictions={result.contradictions} />
              </div>

              <GraphPanel graph={result.graph} />
              <ExtractedFacts facts={result.extracted_facts} />
              <InvestigationReport report={result.investigation_report} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <AIAssistant />
    </div>
  );
}

export default App;
