import React, { useState } from "react";
import WomenSnapQuestion from "../components/WomenSnapQuestion";
import PersonaProgressBar from "../components/PersonaProgressBar";
import { womenQuestions } from "../data/womenQuestions";
import { womenSubgroupQuestions } from "../data/womenSubgroupQuestions";
import {
  calculateWomenGroup,
  calculateWomenFinalPersona,
} from "../utils/personaScoring";
import "../persona.css";

const WomenPersonaTestPage = ({ onComplete, onBack }) => {
  const [phase, setPhase] = useState("groupTest");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [groupResult, setGroupResult] = useState(null);
  const [subgroupAnswer, setSubgroupAnswer] = useState(null);

  const currentQuestion = womenQuestions[currentIndex];
  const selectedOption = answers[currentIndex];

  const subgroupQuestion = groupResult
    ? womenSubgroupQuestions[groupResult.group]
    : null;

  const handleGroupSelect = (option) => {
    const nextAnswers = [...answers];
    nextAnswers[currentIndex] = option;
    setAnswers(nextAnswers);

    const isLastQuestion = currentIndex === womenQuestions.length - 1;

    if (isLastQuestion) {
      const nextGroupResult = calculateWomenGroup(nextAnswers);
      setGroupResult(nextGroupResult);
      setPhase("groupResult");
      return;
    }

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
    }, 180);
  };

  const handleSubgroupSelect = (option) => {
    setSubgroupAnswer(option);

    const finalResult = calculateWomenFinalPersona({
      groupResult,
      subgroupAnswer: option,
    });

    if (onComplete) {
      onComplete(finalResult);
    }
  };

  const handlePrev = () => {
    if (phase === "subgroupTest") {
      setPhase("groupResult");
      return;
    }

    if (phase === "groupResult") {
      setPhase("groupTest");
      setCurrentIndex(womenQuestions.length - 1);
      return;
    }

    if (currentIndex === 0) {
      if (onBack) onBack();
      return;
    }

    setCurrentIndex((prev) => prev - 1);
  };

  if (phase === "groupResult" && groupResult) {
    return (
      <div className="women-persona-page">
        <div className="content-wrapper women-result-wrapper">
          <div className="women-group-result-card fade-in">
            <p className="result-label">당신의 여성복 스타일 그룹은</p>

            <div className="women-result-group">
              <span className="women-result-emoji">
                {groupResult.groupInfo?.emoji}
              </span>
              <span>GROUP {groupResult.groupInfo?.id}</span>
            </div>

            <h1 className="result-title-main women-result-title">
              {groupResult.groupInfo?.label}
            </h1>

            <p className="women-result-subtitle">
              {groupResult.groupInfo?.name}
            </p>

            <div className="women-group-persona-list">
              {groupResult.groupInfo?.personas.map((persona) => (
                <span key={persona} className="women-keyword">
                  {persona}
                </span>
              ))}
            </div>

            <p className="women-group-guide">
              이제 한 문제만 더 선택하면 세부 페르소나가 확정됩니다.
            </p>
          </div>

          <div className="btn-group-center women-result-actions">
            <button
              type="button"
              className="start-btn"
              onClick={() => setPhase("subgroupTest")}
            >
              세부 페르소나 찾기
            </button>
          </div>

          <button type="button" className="back-btn" onClick={handlePrev}>
            이전 질문으로
          </button>
        </div>
      </div>
    );
  }

  if (phase === "subgroupTest" && subgroupQuestion) {
    return (
      <div className="women-persona-page">
        <div className="content-wrapper women-persona-wrapper">
          <WomenSnapQuestion
            question={subgroupQuestion}
            selectedOptionId={subgroupAnswer?.id}
            onSelect={handleSubgroupSelect}
          />

          <button type="button" className="back-btn" onClick={handlePrev}>
            그룹 결과로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="women-persona-page">
      <div className="content-wrapper women-persona-wrapper">
        <PersonaProgressBar
          current={currentIndex + 1}
          total={womenQuestions.length}
        />

        <WomenSnapQuestion
          question={currentQuestion}
          selectedOptionId={selectedOption?.id}
          onSelect={handleGroupSelect}
        />

        <button type="button" className="back-btn" onClick={handlePrev}>
          이전으로
        </button>
      </div>
    </div>
  );
};

export default WomenPersonaTestPage;