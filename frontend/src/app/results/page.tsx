'use client';

import { useEffect, useState } from 'react';
import { Answer, answerOptions, questions } from '../../lib/questionnaire';

type Saved = {
  result: { screening_label: string };
  answers: Answer[];
  score: number;
  assessment: { duration: string; settings: string[]; areas: string[]; strengths: string[]; regression: string; previousSupport: string };
};

function reportItems(values: string[]) {
  return values.length ? <ul className="summary-list">{values.map((value) => <li key={value}>{value}</li>)}</ul> : <p>None selected.</p>;
}

export default function Results() {
  const [saved, setSaved] = useState<Saved | null>(null);
  useEffect(() => {
    const raw = sessionStorage.getItem('autinsight:last_result');
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as Partial<Saved>;
        if (parsed.result && parsed.assessment && typeof parsed.score === 'number' && Array.isArray(parsed.answers)) setSaved(parsed as Saved);
        else sessionStorage.removeItem('autinsight:last_result');
      }
      catch { sessionStorage.removeItem('autinsight:last_result'); }
    }
  }, []);

  if (!saved) return <main className="flow-shell"><div className="eyebrow">Your caregiver summary</div><h1>There isn’t a summary in this browser tab yet.</h1><p>Complete the caregiver questionnaire first. The summary is kept only for this tab session.</p><a className="button" href="/screening">Begin the questions</a></main>;

  const result = saved.result;
  const positive = result.screening_label.toLowerCase().includes('positive');
  const assessment = saved.assessment;
  const areasToExplore = questions.flatMap((question, index) => {
    const answer = saved.answers[index];
    const agrees = answer === 'definitely-agree' || answer === 'slightly-agree';
    const possibleDifficulty = [2, 3, 5, 7, 8].includes(index) ? !agrees : [4, 6, 9].includes(index) ? agrees : false;
    return possibleDifficulty ? [question.topic] : [];
  });

  return <main className="report-shell">
    <div className="eyebrow">Your caregiver summary</div>
    <h1>A starting point for understanding your child.</h1>
    <p className="lead">This summary reflects the answers and observations you shared. It is not a diagnosis and cannot tell you for certain whether your child is autistic.</p>

    <section className={`signal-card ${positive ? 'signal-positive' : 'signal-neutral'}`} aria-labelledby="signal-heading">
      <div className="signal-top"><span className="signal-icon" aria-hidden="true">{positive ? '↗' : '◎'}</span><div><div className="eyebrow">Your screening summary</div><h2 id="signal-heading">{positive ? 'Some answers highlight areas worth discussing' : 'Your answers do not settle whether autism is present'}</h2></div></div>
      <p>{positive ? 'Your responses include several developmental areas that may be useful to explore with a professional who knows your child. This is a prompt for a conversation, not a conclusion about your child.' : 'This response pattern does not rule out autism. Children can have support needs that are not captured by a short questionnaire, and your observations still matter.'}</p>
      {positive ? <p className="recommendation"><strong>Consider discussing a developmental assessment</strong> with your child’s pediatrician or another qualified child-development professional, especially if you or people who know your child share concerns.</p> : <p className="recommendation"><strong>A lower score does not rule out autism.</strong> If you have concerns about your child’s development or behavior, discuss them with a qualified professional regardless of this result.</p>}
    </section>

    <section className="report-section" aria-labelledby="answers-explained-heading">
      <div className="eyebrow">Understanding your child’s development</div><h2 id="answers-explained-heading">What each area may look like in daily life</h2>
      <p>Autism can shape how a child communicates, connects with people, responds to sensory experiences, and handles routines or change. Every child is different, and these characteristics can also occur in children who are not autistic. The notes below explain each area, how it may show up in daily life, and ideas you may wish to discuss or try. One answer cannot identify autism or predict a child’s future. <a href="https://www.cdc.gov/autism/signs-symptoms/" target="_blank" rel="noreferrer">CDC: autism characteristics</a> · <a href="https://www.nhs.uk/conditions/autism/supporting-a-child/" target="_blank" rel="noreferrer">NHS: supporting an autistic child</a>.</p>
      <div className="caregiver-answer-list">{questions.map((question, index) => {
        const answer = saved.answers[index];
        const selected = answerOptions.find((option) => option.value === answer)?.label ?? 'Not available';
        const agrees = answer === 'definitely-agree' || answer === 'slightly-agree';
        return <article className="caregiver-answer-card" key={`question-${index + 1}`}>
          <div className="caregiver-answer-top"><div><span className="eyebrow">Area {index + 1} · {question.topic}</span><h3>{question.text}</h3></div><span className="caregiver-selected">Your answer: {selected}</span></div>
          <p className="caregiver-reflection">{answer ? (agrees ? question.yes : question.no) : 'No response was available for this question.'}</p>
          <div className="caregiver-meaning"><strong>What this area can mean</strong><p>{question.meaning}</p></div>
          <div className="caregiver-meaning"><strong>Ways to support or explore it</strong><p>{question.support}</p></div>
        </article>;
      })}</div>
      <div className="explain-callout"><strong>Your overall answer pattern</strong><p>{areasToExplore.length ? <>Your responses may be worth exploring further around {areasToExplore.join(', ')}. These answers are starting points for noticing what happens in daily life, not proof of a developmental condition. A child’s strengths, preferences, age, experiences, and the situation all matter.</> : 'Your responses did not highlight a specific difficulty among these questions. That does not rule out autism or other support needs; a child’s strengths, preferences, age, experiences, and the situation all matter.'} If any area is affecting your child’s communication, friendships, learning, comfort, or everyday routines—or if you remain concerned—share specific examples with your child’s pediatrician or another qualified developmental professional.</p></div>
    </section>

    <section className="report-section">
      <div className="eyebrow">Your observations</div><h2>What you told us about your child</h2>
      <p>These observations help you prepare for a conversation. They were not sent to the model and did not change the model result.</p>
      <div className="context-grid"><article className="context-card"><h3>How long</h3><p>{assessment.duration || 'Not provided'}</p></article><article className="context-card"><h3>Where noticed</h3>{reportItems(assessment.settings)}</article><article className="context-card"><h3>Areas to discuss</h3>{reportItems(assessment.areas)}</article><article className="context-card"><h3>Strengths to share</h3>{reportItems(assessment.strengths)}</article><article className="context-card"><h3>Previous support</h3><p>{assessment.previousSupport || 'Not provided'}</p></article></div>
      {assessment.regression === 'Yes' && <div className="inline-alert"><strong>You noted a loss of skills.</strong> Please contact your child’s healthcare professional promptly to discuss this change.</div>}
    </section>

    <section className="next-steps" aria-labelledby="next-heading"><div className="eyebrow">What you can do next</div><h2 id="next-heading">Small, practical next steps</h2><ol><li><strong>Talk with your child’s healthcare professional.</strong> Share what you have noticed at home and in other settings. You can ask whether a comprehensive developmental evaluation or referral is appropriate.</li><li><strong>Bring concrete examples.</strong> Note what happened, when it happens, what helps, and your child’s strengths. Ask a teacher or caregiver for their observations if you feel comfortable.</li><li><strong>Ask about support while you wait.</strong> A professional can discuss communication, learning, sleep, sensory, or daily-living supports based on your child’s needs.</li><li><strong>Trust your concern.</strong> A screening result should not be used to dismiss concerns or delay seeking advice.</li></ol><p className="source-note">For general information: <a href="https://www.cdc.gov/autism/diagnosis/index.html" target="_blank" rel="noreferrer">CDC: screening and diagnosis</a> · <a href="https://www.nice.org.uk/guidance/cg128/chapter/Recommendations" target="_blank" rel="noreferrer">NICE: recognition and referral guidance</a>.</p></section>

    <section className="disclaimer"><strong>Please remember</strong><p>AutInsight is a final-year research prototype, not a diagnostic or clinical decision tool. It has not been validated for use with families, and its model output does not indicate a clinical probability. A qualified professional should assess developmental concerns.</p><p>Only age and scored questionnaire answers were sent to the model. Your caregiver observations are stored in this browser tab for this summary and are not sent to the model. Avoid entering identifying information.</p></section>
    <div className="button-row report-actions"><a className="button secondary-button" href="/screening">Start a new summary</a><button className="button secondary-button" type="button" onClick={() => window.print()}>Print this summary</button><a className="button" href="/results/understand">Understand this summary in detail <span aria-hidden="true">→</span></a></div>
  </main>;
}
