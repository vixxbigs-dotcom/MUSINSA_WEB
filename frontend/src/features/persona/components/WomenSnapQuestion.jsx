import React from "react";

const WomenSnapQuestion = ({ question, selectedOptionId, onSelect }) => {
  const isSubgroup = question.layout === "subgroup";

  return (
    <div className="women-question-block fade-in">
      <p className="q-count">
        {isSubgroup
          ? "SUB PERSONA TEST"
          : `QUESTION ${String(question.id).padStart(2, "0")}`}
      </p>

      <h2 className="question-text women-question-title">
        {question.title}
      </h2>

      <div className={`women-snap-grid ${isSubgroup ? "subgroup-grid" : ""}`}>
        {question.options.map((option) => {
          const isSelected = selectedOptionId === option.id;

          return (
            <button
              key={option.id}
              type="button"
              className={`women-snap-card ${isSelected ? "selected" : ""}`}
              onClick={() => onSelect(option)}
              aria-label={`${option.label || option.persona || option.group} 선택`}
            >
              <div className="women-snap-image-box">
                <img
                  src={option.image}
                  alt={`${option.label || option.persona || option.group} 스타일 스냅`}
                  className="women-snap-image"
                />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default WomenSnapQuestion;