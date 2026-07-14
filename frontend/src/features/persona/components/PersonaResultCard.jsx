import React from "react";

const PersonaResultCard = ({ result }) => {
  if (!result) return null;

  const { groupInfo, personaInfo, persona } = result;

  return (
    <div className="women-result-card fade-in">
      <p className="result-label">당신의 여성복 스타일 페르소나는</p>

      <div className="women-result-group">
        <span className="women-result-emoji">{groupInfo?.emoji}</span>
        <span>
          GROUP {groupInfo?.id} · {groupInfo?.label}
        </span>
      </div>

      <h1 className="result-title-main women-result-title">
        {persona}
      </h1>

      <p className="women-result-subtitle">
        {personaInfo?.subtitle}
      </p>

      <p className="persona-desc women-result-description">
        {personaInfo?.description}
      </p>

      <div className="women-keyword-list">
        {personaInfo?.keywords?.map((keyword) => (
          <span key={keyword} className="women-keyword">
            #{keyword}
          </span>
        ))}
      </div>
    </div>
  );
};

export default PersonaResultCard;