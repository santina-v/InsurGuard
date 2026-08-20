import React, { useEffect, useRef, useState, useCallback } from "react";
import { motion } from "framer-motion";
import ForceGraph2D from "react-force-graph-2d";

function GraphPanel({ graph }) {
  const containerRef = useRef(null);
  const graphRef = useRef(null);
  const [graphWidth, setGraphWidth] = useState(900);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setGraphWidth(Math.max(350, containerRef.current.clientWidth));
      }
    };
    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  const drawNode = useCallback((node, ctx, globalScale) => {
    const radius = node.type === "claim" ? 12 : node.type === "document" ? 8 : 4;
    const type = String(node.type || "").toLowerCase();
    const isSelected = selectedNode && selectedNode.id === node.id;

    ctx.beginPath();
    ctx.arc(node.x, node.y, radius + (isSelected ? 2 : 0), 0, 2 * Math.PI);

    if (type === "claim") ctx.fillStyle = "#8b5cf6";
    else if (type === "document") ctx.fillStyle = "#06b6d4";
    else ctx.fillStyle = "#64748b";

    ctx.fill();

    ctx.strokeStyle = isSelected ? "#ffffff" : "#1e293b";
    ctx.lineWidth = isSelected ? 2 : 1.5;
    ctx.stroke();

    if (type === "claim" || type === "document" || isSelected) {
      let label = "";
      if (type === "claim") label = "CLAIM";
      else if (type === "document") {
        if (node.id === "police_report") label = "Police Report";
        else if (node.id === "medical_report") label = "Medical Report";
        else if (node.id === "repair_invoice") label = "Repair Invoice";
        else label = node.id;
      } else label = node.field || node.id;

      const fontSize = type === "claim" ? 14 / globalScale : 12 / globalScale;
      ctx.font = `600 ${fontSize}px Inter, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "#f1f5f9";
      ctx.fillText(label, node.x, node.y + radius + 4);
    }
  }, [selectedNode]);

  if (!graph || !graph.nodes) return null;

  const filteredNodes = graph.nodes.filter((node) => filter === "all" || node.type === filter);
  const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));
  const links = graph.edges || graph.links || [];
  const filteredLinks = links.filter((link) =>
    filteredNodeIds.has(typeof link.source === "object" ? link.source.id : link.source) &&
    filteredNodeIds.has(typeof link.target === "object" ? link.target.id : link.target)
  );

  const graphData = { nodes: filteredNodes, links: filteredLinks };

  const handleZoomIn = () => graphRef.current?.zoom(graphRef.current.zoom() * 1.2, 400);
  const handleZoomOut = () => graphRef.current?.zoom(graphRef.current.zoom() / 1.2, 400);
  const handleZoomReset = () => graphRef.current?.zoomToFit(400);

  return (
    <motion.section
      className="result-card graph-panel"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.5 }}
    >
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">AGENT 3</span>
          <h2>Risk Knowledge Graph</h2>
          <p>Visual representation of claim relationships</p>
        </div>
        <select
          className="graph-filter-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All Nodes</option>
          <option value="claim">Claims Only</option>
          <option value="document">Documents Only</option>
          <option value="fact">Facts Only</option>
        </select>
      </div>

      <div className="graph-legend">
        <div className="legend-item"><span className="legend-dot" style={{ background: "#8b5cf6" }} /> Claim</div>
        <div className="legend-item"><span className="legend-dot" style={{ background: "#06b6d4" }} /> Document</div>
        <div className="legend-item"><span className="legend-dot" style={{ background: "#64748b" }} /> Extracted Fact</div>
      </div>

      <div className="graph-container" ref={containerRef}>
        <div className="graph-controls">
          <button className="graph-control-btn" onClick={handleZoomIn}>+</button>
          <button className="graph-control-btn" onClick={handleZoomOut}>−</button>
          <button className="graph-control-btn" onClick={handleZoomReset}>⛶</button>
        </div>

        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={graphWidth}
          height={500}
          backgroundColor="#0a0f1a"
          nodeCanvasObject={drawNode}
          nodeCanvasObjectMode={() => "replace"}
          linkColor={() => "rgba(6, 182, 212, 0.3)"}
          linkWidth={1.5}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkLabel={(link) => (link.relation ? link.relation.replaceAll("_", " ") : "")}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.35}
          cooldownTicks={150}
          onNodeClick={(node) => setSelectedNode(node)}
        />
      </div>

      {selectedNode && (
        <motion.div
          className="selected-node-card"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
            <div>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase" }}>{selectedNode.type}</span>
              <h3 style={{ margin: 0, fontSize: "15px" }}>{selectedNode.field || selectedNode.id}</h3>
            </div>
            <button onClick={() => setSelectedNode(null)} style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: 18 }}>×</button>
          </div>
          {selectedNode.value !== undefined && <p style={{ fontSize: "13px", margin: "0 0 8px 0" }}><strong>Value:</strong> {selectedNode.value}</p>}
          <p style={{ fontSize: "13px", margin: 0 }}><strong>ID:</strong> {selectedNode.id}</p>
        </motion.div>
      )}
    </motion.section>
  );
}

export default GraphPanel;
