export type Answer = 'definitely-agree' | 'slightly-agree' | 'slightly-disagree' | 'definitely-disagree';

export const answerOptions: { value: Answer; label: string }[] = [
  { value: 'definitely-agree', label: 'Definitely agree' },
  { value: 'slightly-agree', label: 'Slightly agree' },
  { value: 'slightly-disagree', label: 'Slightly disagree' },
  { value: 'definitely-disagree', label: 'Definitely disagree' },
];

// Caregiver-friendly paraphrases of the AQ-10 Child Version items. Keep the
// original item order because the trained UCI model consumes A1–A10 scores.
export const questions = [
  { text: 'Does your child notice quiet sounds that other people often miss?', scoredOn: 'agree', topic: 'noticing sounds', yes: 'You notice that your child may pick up quiet sounds that others miss.', no: 'You do not usually notice your child picking up quiet sounds that others miss.', meaning: 'Children vary in how strongly they notice sounds. Noticing a sound is not a problem by itself; what matters is whether the sound feels uncomfortable, distracts your child, or affects activities.', support: 'Notice which sounds stand out and ask your child how they feel. If a setting is uncomfortable, consider reducing background noise or offering a quieter place when practical.' },
  { text: 'Does your child usually focus on the whole picture more than the small details?', scoredOn: 'disagree', topic: 'details and the overall picture', yes: 'You describe your child as usually taking in the overall picture more than small details.', no: 'You describe your child as often noticing details rather than the overall picture.', meaning: 'Some children naturally focus on details; others first notice the big picture. A detail-focused style can be a strength, though your child may sometimes benefit from help connecting details to the main idea or task.', support: 'When giving instructions, try stating the main idea first and then listing the steps. Ask what your child has noticed and build from that.' },
  { text: 'In a group, can your child follow several people’s conversations at once?', scoredOn: 'disagree', topic: 'group conversations', yes: 'You report that your child can usually keep track of several conversations in a group.', no: 'You report that keeping track of several conversations in a group may be difficult for your child.', meaning: 'Group conversations move quickly and include background noise, changing speakers, and unwritten turn-taking cues. A child who finds this hard may miss parts of what is said or choose to step away; that does not necessarily mean they are uninterested in people.', support: 'Try quieter one-to-one conversations, smaller groups, or shared activities. Give your child time to respond and check whether they heard what was said.' },
  { text: 'Does your child find it easy to switch from one activity to another?', scoredOn: 'disagree', topic: 'switching activities', yes: 'You report that switching from one activity to another is usually manageable for your child.', no: 'You report that moving from one activity to another may be hard for your child.', meaning: 'Changing activities can require stopping something absorbing, shifting attention, and working out what happens next. If this is hard, everyday transitions such as leaving home, ending play, or starting homework may take more time or cause stress.', support: 'A brief warning, a visual schedule, or a clear first-then explanation may make the next step more predictable. Notice which transitions are hardest and what helps.' },
  { text: 'Does your child have difficulty keeping a conversation going with other children?', scoredOn: 'agree', topic: 'conversation with other children', yes: 'You report that your child may find the back-and-forth of conversation with other children difficult.', no: 'You report that keeping a conversation going with other children is usually manageable for your child.', meaning: 'Conversation involves more than speaking: children may need to notice when to take a turn, respond to another person, or shift topics. Difficulty with this can make joining peers tiring or confusing, even when a child wants company.', support: 'Use shared interests or activities as a natural starting point. Allow time to answer, model taking turns without pressure, and ask your child what makes talking with peers easier.' },
  { text: 'Is your child comfortable with casual small talk?', scoredOn: 'disagree', topic: 'small talk', yes: 'You report that casual small talk is usually comfortable for your child.', no: 'You report that casual small talk may feel awkward, unclear, or tiring for your child.', meaning: 'Small talk often relies on social conventions that are not stated directly. A child may prefer conversations with a clear purpose or a familiar topic; this alone does not show whether they want friendships or connection.', support: 'Try conversation through a shared activity or an interest your child enjoys. Clear, specific questions can be easier than expecting a child to know how to begin an open-ended chat.' },
  { text: 'When hearing a story, does your child find it difficult to work out how a character feels or what they intend?', scoredOn: 'agree', topic: 'characters’ feelings and intentions', yes: 'You report that your child can usually work out a story character’s feelings or intentions.', no: 'You report that inferring a character’s feelings or intentions may be difficult for your child.', meaning: 'Stories sometimes expect readers to infer feelings from actions, tone, or context. Finding this hard may also make indirect hints or misunderstandings in everyday situations harder to interpret. It does not mean a child lacks feelings or cares less about others.', support: 'Pause during a story and talk through clues: what happened, what the character said, and what different feelings might fit. Treat answers as possibilities, not a test with only one right response.' },
  { text: 'When your child was in preschool, did they enjoy make-believe games with other children?', scoredOn: 'disagree', topic: 'pretend play', yes: 'You remember that your child enjoyed make-believe games with other children in preschool.', no: 'You remember that your child may not have enjoyed make-believe games with other children in preschool.', meaning: 'Children differ in pretend play. Some prefer predictable, factual, hands-on, or solo play. If joining pretend play was difficult, it may have affected one way of connecting with peers, but it does not tell the whole story of a child’s imagination or ability to play.', support: 'Join the kind of play your child already enjoys, follow their lead, and add small imaginative ideas only if welcome. Shared enjoyment matters more than a particular style of play.' },
  { text: 'Can your child usually work out what someone may be thinking or feeling from their face?', scoredOn: 'disagree', topic: 'facial expressions', yes: 'You report that your child can usually use someone’s facial expression to guess what they may be feeling.', no: 'You report that reading feelings from someone’s face may be difficult for your child.', meaning: 'Faces are only one source of information about feelings; words, tone, gestures, and the situation also matter. A child who does not readily read facial cues may miss indirect signals, but this does not mean they lack empathy or affection.', support: 'Name feelings and explain the clues you noticed in everyday situations. You can also use direct words rather than relying on hints, and accept that people express feelings differently.' },
  { text: 'Does your child find it hard to make new friends?', scoredOn: 'agree', topic: 'making friends', yes: 'You report that making new friends may be hard for your child.', no: 'You report that making new friends is not usually hard for your child.', meaning: 'Making friends can involve finding shared interests, starting conversations, reading social cues, and handling the uncertainty of a new group. Difficulty may lead to feeling left out if the child wants more connection, but some children are content with a small circle or time alone.', support: 'Ask your child whether they want help meeting others. Consider a small, structured activity around an interest they enjoy, and talk with school staff if they want friends but are often left out.' },
] as const;

export function scoreAnswers(answers: Answer[]): number[] {
  return answers.map((answer, index) => {
    const agrees = answer === 'definitely-agree' || answer === 'slightly-agree';
    return (questions[index].scoredOn === 'agree' ? agrees : !agrees) ? 1 : 0;
  });
}

export function answerReflection(index: number, answer: Answer): string {
  const agrees = answer === 'definitely-agree' || answer === 'slightly-agree';
  const strength = answer.startsWith('definitely') ? 'strongly' : 'somewhat';
  const reflection = agrees ? questions[index].yes : questions[index].no;
  return `${strength === 'strongly' ? 'You strongly ' : 'You somewhat '}${agrees ? 'agree' : 'disagree'} with the statement. ${reflection}`;
}

export const featureLabels: Record<string, string> = {
  age: 'Child’s age',
  gender: 'Gender field',
  jaundice: 'Jaundice history field',
  family_history: 'Family history field',
  ethnicity: 'Ethnicity field',
  country: 'Country field',
  used_app_before: 'Prior app-use field',
  who_completed: 'Respondent field',
};

export function describeFeature(feature: string): { title: string; detail: string } {
  const normalized = feature.toLowerCase();
  const item = normalized.match(/a(?:_|)([1-9]|10)(?:_|$)/);
  if (item) {
    const index = Number(item[1]) - 1;
    return { title: `Question ${index + 1}`, detail: questions[index].text };
  }
  const key = Object.keys(featureLabels).find((name) => normalized.includes(name));
  return {
    title: key ? featureLabels[key] : feature.replaceAll('_', ' '),
    detail: 'This context field influenced the model’s source-dataset class.',
  };
}
