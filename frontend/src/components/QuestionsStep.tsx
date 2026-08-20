import type { FollowUpQuestion } from '../lib/types'

interface Props {
  questions: FollowUpQuestion[]
  answers: Record<string, string>
  onAnswer: (id: string, value: string) => void
  onContinue: () => void
}

export function QuestionsStep({ questions, answers, onAnswer, onContinue }: Props) {
  const answeredAll = questions.every((question) => answers[question.id])
  return (
    <section className="card">
      <h2>A few questions about your plan</h2>
      {questions.map((question) => (
        <div className="field" key={question.id}>
          <label>{question.question}</label>
          <div className="chips">
            {question.options.map((option) => (
              <button
                key={option}
                type="button"
                className={answers[question.id] === option ? 'chip selected' : 'chip'}
                onClick={() => onAnswer(question.id, option)}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      ))}
      <button className="primary" disabled={!answeredAll} onClick={onContinue}>
        Show travel options
      </button>
    </section>
  )
}
