'use strict';

const { parseFraction, equalFraction } = require('./fractions');

// Game state machine per the State Diagram:
//   Playing -> Paused (pause()), Paused -> Playing (resume()),
//   Playing -> GameOver (gameOver()).
const STATE = {
  PLAYING: 'Playing',
  PAUSED: 'Paused',
  GAME_OVER: 'GameOver',
};

class Game {
  constructor(id, questions) {
    this.id = id;
    this.questions = questions; // array of question objects (already resolved copies)
    this.index = 0;
    this.state = STATE.PLAYING;
    this.correct = 0;
    this.answers = []; // { questionId, submitted, correct }
  }

  currentQuestion() {
    if (this.state !== STATE.PLAYING) {
      return null;
    }
    if (this.index >= this.questions.length) {
      return null;
    }
    return this.questions[this.index];
  }

  pause() {
    if (this.state !== STATE.PLAYING) {
      throw new Error(`cannot pause from state ${this.state}`);
    }
    this.state = STATE.PAUSED;
    return this.state;
  }

  resume() {
    if (this.state !== STATE.PAUSED) {
      throw new Error(`cannot resume from state ${this.state}`);
    }
    this.state = STATE.PLAYING;
    return this.state;
  }

  submitAnswer(submitted) {
    if (this.state !== STATE.PLAYING) {
      throw new Error(`cannot submit answer in state ${this.state}`);
    }
    const q = this.currentQuestion();
    if (!q) {
      throw new Error('no current question');
    }
    const parsedSubmitted = parseFraction(String(submitted));
    let result;
    if (parsedSubmitted === null) {
      result = false;
    } else {
      const expected = parseFraction(q.answer);
      result = expected !== null && equalFraction(parsedSubmitted, expected);
    }
    if (result) {
      this.correct += 1;
    }
    this.answers.push({ questionId: q.id, submitted, correct: result });
    this.index += 1;
    if (this.index >= this.questions.length) {
      this.state = STATE.GAME_OVER;
    }
    return { correct: result, gameOver: this.state === STATE.GAME_OVER };
  }

  gameOver() {
    if (this.state !== STATE.PLAYING) {
      throw new Error(`cannot end game from state ${this.state}`);
    }
    this.state = STATE.GAME_OVER;
    return this.state;
  }

  score() {
    if (this.state !== STATE.GAME_OVER) {
      throw new Error('score is final only after game over');
    }
    return { correct: this.correct, total: this.questions.length };
  }
}

module.exports = { Game, STATE };
