'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Answer, answerOptions, questions, scoreAnswers } from '../../lib/questionnaire';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const settingsOptions = ['At home', 'At school or early learning', 'In the community', 'In more than one setting', 'Not sure'];
const areaOptions = [
  'Understanding or using communication',
  'Back-and-forth interaction or connecting with others',
  'Peer play or making friends',
  'Sensory experiences',
  'Changes, routines, or transitions',
  'Strong interests or repeated play',
  'Learning, sleep, or everyday activities',
  'No specific areas noticed',
  'Not sure yet',
];
const strengthOptions = ['Interests and knowledge', 'Memory', 'Creativity or imagination', 'Noticing patterns or details', 'Persistence', 'Warmth or care for others', 'Movement or practical skills', 'Something else / still learning'];

type Assessment = {
  duration: string;
  settings: string[];
  areas: string[];
  strengths: string[];
  regression: string;
  previousSupport: string;
};

function CheckGroup({ title, help, options, values, onToggle }: {
  title: string;
  help?: string;
  options: string[];
  values: string[];
  onToggle: (value: string) => void;
}) {
  return <fieldset className="choice-group"><legend>{title}</legend>{help && <p className="field-help">{help}</p>}<div className="check-grid">{options.map((option) => <label className="check-option" key={option}><input type="checkbox" checked={values.includes(option)} onChange={() => onToggle(option)} /> <span>{option}</span></label>)}</div></fieldset>;
}

export default function Screening() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [age, setAge] = useState('');
  const [answers, setAnswers] = useState<(Answer | '')[]>(Array(10).fill(''));
  const [assessment, setAssessment] = useState<Assessment>({ duration: '', settings: [], areas: [], strengths: [], regression: '', previousSupport: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  function toggle(field: 'settings' | 'areas' | 'strengths', value: string) {
    setAssessment((previous) => ({ ...previous, [field]: previous[field].includes(value) ? previous[field].filter((item) => item !== value) : [...previous[field], value] }));
  }

  function continueToAssessment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    const years = Number(age);
    if (!Number.isFinite(years) || years < 4 || years > 11) {
      setError('This child-version questionnaire is intended for ages 4–11. If your child is outside that range, please discuss your concerns with a health professional instead.');
      return;
    }
    if (answers.some((answer) => !answer)) {
      setError('Please choose one response for each of the ten questions.');
      return;
    }
    setStep(2);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function finishAssessment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    if (!assessment.duration || !assessment.regression) {
      setError('Please answer how long you have noticed these differences and whether your child has lost any skills.');
      return;
    }
    setBusy(true);
    try {
      const response = await fetch(`${API}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: Number(age), gender: 'unknown', jaundice: 'unknown', family_asd: 'unknown', questions: scoreAnswers(answers as Answer[]) }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : 'The screening service is unavailable. Please try again shortly.');
      sessionStorage.setItem('autinsight:last_result', JSON.stringify({ result: payload, age: Number(age), answers, score: scoreAnswers(answers as Answer[]).reduce((sum, value) => sum + value, 0), assessment }));
      router.push('/results');
    } catch (caught) {
      setError(caught instanceof TypeError ? `Could not reach the screening service at ${API}. Check that the API server is running and reload the page. If the problem continues, restart the backend so it picks up the local browser address.` : caught instanceof Error ? caught.message : 'Could not reach the screening service. Please check that both app servers are running.');
    } finally {
      setBusy(false);
    }
  }

  return <main className="flow-shell">
    <div className="eyebrow">Caregiver guide · Step {step} of 2</div>
    <h1>{step === 1 ? 'Let’s begin with what you have noticed.' : 'Add the context that matters to your family.'}</h1>
    <p className="lead">{step === 1 ? 'Answer based on what you have seen over time, not just today. There are no wrong answers.' : 'These questions help organize a conversation with your child’s care team. They are not scored by the model.'}</p>
    <div className="progress-track" aria-label={`Step ${step} of 2`}><span style={{ width: step === 1 ? '50%' : '100%' }} /></div>

    {step === 1 ? <form onSubmit={continueToAssessment}>
      <section className="soft-callout"><strong>A supportive first look</strong><p>This project uses caregiver-friendly versions of ten items inspired by the AQ-10 Child Version. The wording has been adapted and the online experience has not been validated as a clinical questionnaire. It cannot diagnose autism or rule it out. The source instrument is intended for children aged 4–11; if your child has a known learning disability, discuss the result with a qualified professional because the source guide may not apply.</p></section>
      <label className="field age-field">How old is your child? <span className="field-help">Age in years (4–11)</span><input aria-label="Child age in years" type="number" min="4" max="11" step="1" value={age} onChange={(event) => setAge(event.target.value)} required /></label>
      <div className="question-list">{questions.map((question, index) => <fieldset className="question-card" key={index}><legend><span className="question-number">{index + 1}</span>{question.text}</legend><div className="radio-grid">{answerOptions.map((option) => <label className={`radio-option ${answers[index] === option.value ? 'selected' : ''}`} key={option.value}><input type="radio" name={`q${index + 1}`} value={option.value} checked={answers[index] === option.value} onChange={() => setAnswers((previous) => previous.map((answer, itemIndex) => itemIndex === index ? option.value : answer))} /><span>{option.label}</span></label>)}</div></fieldset>)}</div>
      <p className="source-note">Item order and response scoring are aligned to the AQ-10 Child Version. Wording adapted for clarity. <a href="https://northdevoncoastalpcn.nhs.uk/media/hypg30xa/aq-10child-autism.pdf" target="_blank" rel="noreferrer">View the source guide</a>.</p>
      <button className="button" type="submit">Continue to caregiver assessment <span aria-hidden="true">→</span></button>
    </form> : <form onSubmit={finishAssessment}>
      <section className="soft-callout"><strong>Your observations are valuable.</strong><p>You know your child across everyday life. Sharing both strengths and support needs can help a professional understand the whole picture.</p></section>
      <fieldset className="choice-group"><legend>How long have you noticed these differences or concerns?</legend><div className="radio-stack">{['Recently, within the past few months', 'For about 6–12 months', 'For more than a year', 'Since early childhood', 'I’m not sure'].map((item) => <label className={`radio-option ${assessment.duration === item ? 'selected' : ''}`} key={item}><input type="radio" name="duration" value={item} checked={assessment.duration === item} onChange={() => setAssessment((previous) => ({ ...previous, duration: item }))} /><span>{item}</span></label>)}</div></fieldset>
      <CheckGroup title="Where have you noticed them? (Choose any that fit)" options={settingsOptions} values={assessment.settings} onToggle={(value) => toggle('settings', value)} />
      <CheckGroup title="Which areas would you like help understanding? (Choose any that fit)" help="These are conversation topics, not symptoms you need to confirm." options={areaOptions} values={assessment.areas} onToggle={(value) => toggle('areas', value)} />
      <CheckGroup title="What strengths would you like the care team to know about? (Optional)" options={strengthOptions} values={assessment.strengths} onToggle={(value) => toggle('strengths', value)} />
      <fieldset className="choice-group"><legend>Has your child lost words, social abilities, or other skills they used to have?</legend><div className="radio-stack">{['Yes', 'No', 'Not sure'].map((item) => <label className={`radio-option ${assessment.regression === item ? 'selected' : ''}`} key={item}><input type="radio" name="regression" value={item} checked={assessment.regression === item} onChange={() => setAssessment((previous) => ({ ...previous, regression: item }))} /><span>{item}</span></label>)}</div>{assessment.regression === 'Yes' && <p className="inline-alert">Please contact your child’s healthcare professional promptly to discuss a loss of skills.</p>}</fieldset>
      <fieldset className="choice-group"><legend>Have you discussed these concerns with a professional before?</legend><div className="radio-stack">{['Not yet', 'Yes, and we have a follow-up plan', 'We are waiting for an appointment or assessment', 'I’m not sure'].map((item) => <label className={`radio-option ${assessment.previousSupport === item ? 'selected' : ''}`} key={item}><input type="radio" name="support" value={item} checked={assessment.previousSupport === item} onChange={() => setAssessment((previous) => ({ ...previous, previousSupport: item }))} /><span>{item}</span></label>)}</div></fieldset>
      <p className="privacy-note">Please do not enter names or other identifying details. The model receives only age and scored questionnaire answers. Your caregiver observations stay in this browser tab and are not sent to the model.</p>
      <div className="button-row"><button className="button secondary-button" type="button" onClick={() => setStep(1)}>← Back to questions</button><button className="button" type="submit" disabled={busy}>{busy ? 'Preparing your summary…' : 'See the summary and next steps'}</button></div>
    </form>}
    {error && <div className="inline-alert" role="alert">{error}</div>}
  </main>;
}
