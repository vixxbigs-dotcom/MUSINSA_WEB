import React from "react";

const PersonaProgressBar = ({ current, total }) => {
  const progress = total > 0 ? (current / total) * 100 : 0;

  return (
    <div className="women-progress-wrap">
      <div className="women-progress-meta">
        <span>{current}</span>
        <span>{total}</span>
      </div>

      <div className="progress-bar">
        <div className="progress" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
};

export default PersonaProgressBar;