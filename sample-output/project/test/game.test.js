'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { Game, STATE } = require('../lib/game');
const { QuestionRepository } = require('../lib/questions');

function makeQuestions() {
  const repo = new QuestionRepository();
  repo.add({ prompt: '1/2 + 1/4', options: ['3/4'], answer: '3/4' });
  repo.add({ prompt: 'reduce 4/8', options: ['1/2'], answer: '1/2' });
  return repo.list();
}

test('Game starts in Playing state with a current question', () => {
  const game = new Game(1, makeQuestions());
  assert.equal(game.state, STATE.PLAYING);
  assert.equal(game.currentQuestion().prompt, '1/2 + 1/4');
});

test('submitAnswer grades reduced-equivalent fractions', () => {
  const game = new Game(1, makeQuestions());
  const result = game.submitAnswer('6/8'); // equals 3/4
  assert.equal(result.correct, true);
  assert.equal(result.gameOver, false);
});

test('submitAnswer marks incorrect answers and advances', () => {
  const game = new Game(1, makeQuestions());
  const result = game.submitAnswer('1/3');
  assert.equal(result.correct, false);
  assert.equal(game.currentQuestion().prompt, 'reduce 4/8');
});

test('finishing all questions triggers GameOver and final score', () => {
  const game = new Game(1, makeQuestions());
  game.submitAnswer('3/4'); // correct
  game.submitAnswer('1/4'); // incorrect
  assert.equal(game.state, STATE.GAME_OVER);
  assert.deepEqual(game.score(), { correct: 1, total: 2 });
});

test('pause/resume/gameOver transitions follow the State Diagram', () => {
  const game = new Game(1, makeQuestions());
  assert.equal(game.pause(), STATE.PAUSED);
  assert.throws(() => game.submitAnswer('3/4'), /cannot submit/);
  assert.equal(game.resume(), STATE.PLAYING);
  assert.equal(game.gameOver(), STATE.GAME_OVER);
  assert.throws(() => game.gameOver(), /cannot end game/);
});

test('score is unavailable before game over', () => {
  const game = new Game(1, makeQuestions());
  assert.throws(() => game.score(), /final only after game over/);
});

test('submitAnswer rejects invalid fractions as incorrect', () => {
  const game = new Game(1, makeQuestions());
  const result = game.submitAnswer('not-a-fraction');
  assert.equal(result.correct, false);
});

test('QuestionRepository assigns ids and lists questions', () => {
  const repo = new QuestionRepository();
  repo.add({ prompt: 'a', answer: '1/2' });
  repo.add({ prompt: 'b', answer: '2' });
  assert.equal(repo.count(), 2);
  assert.equal(repo.get(1).prompt, 'a');
  assert.equal(repo.get(2).answer, '2');
  assert.equal(repo.list().length, 2);
  assert.equal(repo.get(99), null);
});
