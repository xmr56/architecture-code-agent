'use strict';

const express = require('express');
const { Game } = require('./game');
const { QuestionRepository } = require('./questions');
const { parseFraction } = require('./fractions');

const HELP_TEXT =
  'Space Fractions: answer each fraction question in reduced form, e.g. 3/4 or 4 (for whole numbers).';

function createApp(options = {}) {
  const questions = new QuestionRepository(options.seedQuestions || []);
  const games = new Map();
  let nextGameId = 1;

  const app = express();
  app.use(express.json());

  // FR-1: Play game — start a new game using all available questions.
  app.get('/play', (req, res) => {
    const all = questions.list();
    if (all.length === 0) {
      return res.status(404).json({ error: 'no questions available' });
    }
    const id = nextGameId++;
    const game = new Game(id, all);
    games.set(id, game);
    res.status(200).json({
      gameId: id,
      state: game.state,
      totalQuestions: all.length,
      firstQuestion: game.currentQuestion(),
    });
  });

  // Fetch the current question of a game.
  app.get('/games/:id/question', (req, res) => {
    const game = games.get(Number(req.params.id));
    if (!game) {
      return res.status(404).json({ error: 'game not found' });
    }
    const q = game.currentQuestion();
    if (!q) {
      return res.status(409).json({ error: 'no current question', state: game.state });
    }
    res.json({ gameId: game.id, state: game.state, question: q });
  });

  // Submit an answer for the current question.
  app.post('/games/:id/answer', (req, res) => {
    const game = games.get(Number(req.params.id));
    if (!game) {
      return res.status(404).json({ error: 'game not found' });
    }
    const submitted = req.body && req.body.answer;
    if (submitted === undefined || submitted === null) {
      return res.status(400).json({ error: 'answer is required' });
    }
    try {
      const result = game.submitAnswer(submitted);
      const payload = { gameId: game.id, correct: result.correct, gameOver: result.gameOver };
      if (result.gameOver) {
        payload.score = game.score();
      }
      res.json(payload);
    } catch (err) {
      res.status(409).json({ error: err.message });
    }
  });

  // View score.
  app.get('/games/:id/score', (req, res) => {
    const game = games.get(Number(req.params.id));
    if (!game) {
      return res.status(404).json({ error: 'game not found' });
    }
    try {
      res.json({ gameId: game.id, state: game.state, score: game.score() });
    } catch (err) {
      res.status(409).json({ error: err.message });
    }
  });

  // State transitions (pause/resume/gameOver), mirroring the State Diagram.
  const transition = (action) => (req, res) => {
    const game = games.get(Number(req.params.id));
    if (!game) {
      return res.status(404).json({ error: 'game not found' });
    }
    try {
      const state = game[action]();
      res.json({ gameId: game.id, state });
    } catch (err) {
      res.status(409).json({ error: err.message });
    }
  };
  app.post('/games/:id/pause', transition('pause'));
  app.post('/games/:id/resume', transition('resume'));
  app.post('/games/:id/gameover', transition('gameOver'));

  // Admin: update questions.
  app.post('/admin/questions', (req, res) => {
    const body = req.body || {};
    if (typeof body.prompt !== 'string' || !body.prompt.trim()) {
      return res.status(400).json({ error: 'prompt is required' });
    }
    if (typeof body.answer !== 'string' || parseFraction(body.answer) === null) {
      return res.status(400).json({ error: 'answer must be a valid fraction string' });
    }
    const created = questions.add({
      category: body.category,
      prompt: body.prompt,
      options: body.options,
      answer: body.answer,
    });
    res.status(201).json(created);
  });

  // View help.
  app.get('/help', (req, res) => {
    res.json({ help: HELP_TEXT });
  });

  // Health/metrics endpoint stub for observability hooks.
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', gameCount: games.size, questionCount: questions.count() });
  });

  return { app, questions, games };
}

module.exports = { createApp, HELP_TEXT };
