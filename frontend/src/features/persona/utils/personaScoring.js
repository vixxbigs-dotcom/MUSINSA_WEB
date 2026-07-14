import { WOMEN_PERSONA_GROUPS } from "../data/womenPersonaGroups";
import { WOMEN_PERSONA_DESCRIPTIONS } from "../data/womenPersonaDescriptions";

const GROUP_TIE_PRIORITY = ["C", "A", "D", "B"];

const getTopGroupWithPriority = (groupScores) => {
  return Object.keys(groupScores).sort((a, b) => {
    const scoreDiff = groupScores[b] - groupScores[a];

    if (scoreDiff !== 0) {
      return scoreDiff;
    }

    return GROUP_TIE_PRIORITY.indexOf(a) - GROUP_TIE_PRIORITY.indexOf(b);
  })[0];
};

export const calculateWomenGroup = (answers) => {
  const groupScores = {
    A: 0,
    B: 0,
    C: 0,
    D: 0,
  };

  answers.forEach((answer) => {
    if (!answer?.group) return;
    groupScores[answer.group] = (groupScores[answer.group] || 0) + 1;
  });

  const topGroup = getTopGroupWithPriority(groupScores);
  const groupInfo = WOMEN_PERSONA_GROUPS[topGroup];

  return {
    gender: "women",
    group: topGroup,
    groupInfo,
    groupScores,
    answers,
  };
};

export const calculateWomenFinalPersona = ({ groupResult, subgroupAnswer }) => {
  const finalPersona = subgroupAnswer.persona;
  const personaInfo = WOMEN_PERSONA_DESCRIPTIONS[finalPersona];

  return {
    gender: "women",
    group: groupResult.group,
    groupInfo: groupResult.groupInfo,
    groupScores: groupResult.groupScores,
    persona: finalPersona,
    personaInfo,
    subgroupAnswer,
    answers: groupResult.answers,
  };
};