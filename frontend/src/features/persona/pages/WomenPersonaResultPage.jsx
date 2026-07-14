import React from "react";
import PersonaResultCard from "../components/PersonaResultCard";
import "../persona.css";

const WomenPersonaResultPage = ({
  result,
  onRestart,
  onGoToCollage,
  onBackHome,
}) => {
  if (!result) {
    return (
      <div className="women-persona-page">
        <div className="result-container">
          <p className="result-label">검사 결과가 없습니다.</p>

          <button type="button" className="start-btn" onClick={onRestart}>
            다시 검사하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="women-persona-page">
      <div className="content-wrapper women-result-wrapper">
        <PersonaResultCard result={result} />

        <div className="btn-group-center women-result-actions">
          <button type="button" className="start-btn" onClick={onGoToCollage}>
            추천 코디 보러가기
          </button>

          <button type="button" className="secondary-btn" onClick={onRestart}>
            다시 검사하기
          </button>
        </div>

        <button type="button" className="back-btn" onClick={onBackHome}>
          처음으로 돌아가기
        </button>
      </div>
    </div>
  );
};

export default WomenPersonaResultPage;