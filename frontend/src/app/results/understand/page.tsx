'use client';

import { useEffect, useState } from 'react';
import { Answer, answerOptions, describeFeature, questions, scoreAnswers } from '../../../lib/questionnaire';

type Contribution = { feature: string; contribution: number };
type QuestionContribution = { item: number; contribution: number | null };
type Stored = {
  result: {
    explanation?: Contribution[];
    question_contributions?: QuestionContribution[];
    screening_label?: string;
    model_version?: string;
  };
  age: number;
  answers: Answer[];
  score: number;
};

const researchPlots = [
  { file: 'questionnaire_response_means.png', title: 'Average questionnaire responses in the UCI cohort', text: 'A dataset-level descriptive plot. It summarizes source cohort responses and is not a comparison of your child with a reference population.' },
  { file: 'class_distribution.png', title: 'UCI source label distribution', text: 'Shows how many records carry each dataset label. The labels are generated from the same ten item scores using a threshold rule.' },
  { file: 'age_distribution.png', title: 'Age distribution in the UCI cohort', text: 'Describes the age range represented in the research dataset. It does not establish that the sample represents all children.' },
  { file: 'missingness.png', title: 'Missing data in the UCI cohort', text: 'Shows where values were absent in the source dataset. Model preprocessing handles missing fields using training-fitted imputation.' },
  { file: 'indian_target_distribution.png', title: 'Indian validation cohort diagnoses', text: 'Counts in the separate AIIMS modified INDT-ASD validation cohort. This cohort has a different questionnaire and target and is never pooled with UCI.' },
  { file: 'indian_age_distribution.png', title: 'Age distribution in the Indian cohort', text: 'Descriptive context for the Indian referral cohort; not a general-population age profile.' },
  { file: 'indian_missingness.png', title: 'Missing data in the Indian cohort', text: 'Source-field missingness after data audit. This is a research quality plot, not an individual result.' },
];

function itemNumber(feature: string): number | null {
  const match = feature.toLowerCase().match(/a(?:_|)([1-9]|10)(?:_|$)/);
  return match ? Number(match[1]) : null;
}

export default function Understand() {
  const [saved, setSaved] = useState<Stored | null>(null);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem('autinsight:last_result');
      if (raw) setSaved(JSON.parse(raw) as Stored);
    } catch { setSaved(null); }
  }, []);

  const contributions = saved?.result?.explanation ?? [];
  const questionValues = saved?.result?.question_contributions ?? [];
  const maxContribution = Math.max(
    0.001,
    ...questionValues.flatMap((item) => item.contribution == null ? [] : [Math.abs(item.contribution)]),
    ...contributions.filter((item) => itemNumber(item.feature) != null).map((item) => Math.abs(item.contribution)),
  );
  const scores = saved ? scoreAnswers(saved.answers) : [];
  const total = saved ? (typeof saved.score === 'number' ? saved.score : scores.reduce((sum, value) => sum + value, 0)) : 0;
  const modelSaysYes = (saved?.result?.screening_label ?? '').toLowerCase().includes('positive');

  function contributionFor(index: number): number | null {
    const full = questionValues.find((item) => item.item === index + 1);
    if (full) return full.contribution;
    const legacy = contributions.find((item) => itemNumber(item.feature) === index + 1);
    return legacy?.contribution ?? null;
  }

  return <main className="report-shell explain-page">
    <a className="back-link" href="/results">← Back to your summary</a>
    <div className="eyebrow">A caregiver guide to your screening</div>
    <h1>Understand this summary in detail</h1>
    <p className="lead">Explore what each question is about, how your answer entered the screening, and what the model attribution says. These are clues for understanding and discussion, not a diagnosis or a measure of a child’s worth or potential.</p>

    {saved && <section className="report-section" aria-labelledby="overall-screening-title">
      <div className="eyebrow">Your result at a glance</div><h2 id="overall-screening-title">Overall screening</h2>
      <p>The chart summarizes the questionnaire scoring rule and shows the model’s source-data class separately. The source dataset labels totals of 7 or more as YES. That rule is based on these same ten items; it is not an independent estimate of autism.</p>
      <div className="overall-screening-card">
        <div className="overall-screening-heading"><div><span className="eyebrow">Questionnaire score</span><strong>{total} <small>of 10</small></strong></div><div className={`overall-model-label ${modelSaysYes ? 'is-yes' : 'is-no'}`}><span>Model’s source-data class</span><b>{modelSaysYes ? 'YES pattern' : 'NO pattern'}</b></div></div>
        <div className="score-chart" role="img" aria-label={`Questionnaire score ${total} out of 10. The source dataset's YES threshold is 7.`}>
          <div className="score-chart-track">{Array.from({ length: 10 }, (_, index) => <span key={index} className={`score-chart-cell ${index < total ? 'filled' : ''} ${index === 6 ? 'threshold-cell' : ''}`} />)}</div>
          <div className="score-chart-labels"><span>0</span><span className="threshold-label">7 · source YES threshold</span><span>10</span></div>
        </div>
        <p className="overall-screening-explanation">{total >= 7 ? 'This answer total reaches the source dataset’s YES threshold.' : 'This answer total is below the source dataset’s YES threshold.'} The trained model separately classified this response as the <b>{modelSaysYes ? 'YES' : 'NO'}</b> source-data class. Either output only describes how the responses relate to the research dataset; neither confirms nor rules out autism.</p>
      </div>
    </section>}

    <section className="report-section" aria-labelledby="local-title"><div className="eyebrow">This screening · local TreeSHAP</div><h2 id="local-title">How the model arrived at its class</h2>
      <p>TreeSHAP breaks the model’s output into contributions from its inputs. A bar toward YES pushed this model output toward the UCI dataset’s YES class; a bar toward NO pushed it toward NO. Larger bars had a larger influence on this model output for this screening, relative to the other bars shown. This explains the model’s calculation, not why a child has a characteristic.</p>
      {contributions.length ? <div className="shap-plot" aria-label="Local TreeSHAP contributions for this screening">{contributions.map((item) => { const feature = describeFeature(item.feature); const towardYes = item.contribution > 0; const width = Math.max(2, Math.abs(item.contribution) / Math.max(0.001, ...contributions.map((entry) => Math.abs(entry.contribution))) * 48); const number = itemNumber(item.feature); const response = number ? answerOptions.find((option) => option.value === saved?.answers[number - 1])?.label : undefined; return <div className="shap-row" key={item.feature}><div className="shap-label"><strong>{number ? questions[number - 1].text : feature.title}</strong><span>{response ? `Caregiver response: ${response}` : item.feature.toLowerCase().includes('age') ? `Age entered: ${saved?.age} years` : feature.detail}</span></div><div className="shap-axis"><span className={`shap-bar ${towardYes ? 'positive' : 'negative'}`} style={{ width: `${width}%`, left: towardYes ? '50%' : `calc(50% - ${width}%)` }} /></div><span className={`shap-direction ${towardYes ? 'toward-yes' : 'toward-no'}`}>{towardYes ? 'Toward YES' : 'Toward NO'}</span></div> })}<div className="shap-scale"><span>Toward NO</span><span>0 · no shift</span><span>Toward YES</span></div></div> : <p>Individual TreeSHAP contributions were not available in this saved result.</p>}
      <p className="plot-caption">A positive or negative attribution is not a clinical risk or severity score. The model learned patterns from a dataset whose YES/NO labels are generated from the same ten questionnaire item scores. SHAP describes associations in that model and cannot establish cause.</p>
    </section>

    {saved && <section className="report-section" aria-labelledby="question-guide-title"><div className="eyebrow">Your responses, one by one</div><h2 id="question-guide-title">What each question may tell you to notice</h2>
      <p>Each item below uses the actual question wording. The “screening role” explains how the answer was represented in this tool; the developmental notes explain what caregivers may observe in everyday settings. A single item should not be interpreted on its own.</p>
      <div className="detailed-question-list">{questions.map((question, index) => {
        const answer = saved.answers[index];
        const agrees = answer === 'definitely-agree' || answer === 'slightly-agree';
        const answerLabel = answerOptions.find((option) => option.value === answer)?.label ?? 'Not available';
        const score = scores[index] ?? 0;
        const contribution = contributionFor(index);
        const towardYes = contribution != null && contribution > 0;
        const towardNo = contribution != null && contribution < 0;
        const barWidth = contribution == null ? 0 : Math.min(50, Math.max(2, Math.abs(contribution) / maxContribution * 50));
        return <article className="detailed-question-card" key={`detailed-question-${index + 1}`}>
          <div className="detailed-question-heading"><span className="eyebrow">Developmental area · {question.topic}</span><h3>{question.text}</h3></div>
          <div className="detailed-answer"><span>Your response</span><b>{answerLabel}</b><p>{answer ? (agrees ? question.yes : question.no) : 'No response was available for this item.'}</p></div>
          <div className="detailed-explanation-grid">
            <div><h4>What this trait can mean</h4><p>{question.meaning}</p></div>
            <div><h4>What may help</h4><p>{question.support}</p></div>
          </div>
          <div className="screening-role"><h4>How this response contributes to the screening</h4><p>The tool converts this answer to <b>{score}</b>. A score of 1 adds one point to the UCI questionnaire rule; a score of 0 adds none. The source dataset’s YES label begins at 7 out of 10. “Slightly” and “definitely” responses in the same agree/disagree direction receive the same binary item score here.</p></div>
          <div className="question-shap"><h4>What the model attribution means for this item</h4>{contribution == null ? <p>A question-specific TreeSHAP value is not available for this saved result. The screening-role explanation above remains available.</p> : <><div className="question-shap-row"><span className="question-shap-axis"><i className={towardYes ? 'positive' : towardNo ? 'negative' : 'neutral'} style={{ width: `${barWidth}%`, left: towardYes || !towardNo ? '50%' : `calc(50% - ${barWidth}%)` }} /></span><b>{towardYes ? 'Toward YES' : towardNo ? 'Toward NO' : 'No meaningful shift'}</b></div><p>This question moved the model’s raw output {towardYes ? 'toward' : towardNo ? 'away from' : 'very little relative to'} the source dataset’s YES class (contribution {contribution.toFixed(4)}). A larger absolute value means more influence on this model output for this response compared with smaller item bars. It does not mean this trait is more serious, caused by autism, or clinically important.</p></>}</div>
        </article>;
      })}</div>
    </section>}

    <section className="report-section"><div className="eyebrow">How to read the project’s plots</div><h2>Research figures</h2><p>These figures summarize the datasets used in the project. The Indian dataset is a separate study cohort with a different instrument and outcome; comparisons between the two datasets are not meaningful.</p><div className="research-plot-grid">{researchPlots.map((plot) => <figure className="research-plot-card" key={plot.file}><img src={`/research-plots/${plot.file}`} alt={plot.title} /><figcaption><strong>{plot.title}</strong><span>{plot.text}</span></figcaption></figure>)}</div></section>
    <section className="disclaimer"><strong>Not a diagnosis</strong><p>This research prototype has not been clinically validated for caregiver use. Discuss developmental concerns with a qualified professional regardless of the model output.</p></section>
    <div className="button-row report-actions"><a className="button secondary-button" href="/results">Back to your summary</a><button className="button" type="button" onClick={() => window.print()}>Print this explanation</button></div>
  </main>;
}
