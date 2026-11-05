'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');

const { createApp } = require('../lib/app');

function startServer(app) {
  return new Promise((resolve) => {
    const server = http.createServer(app);
    server.listen(0, () => resolve(server));
  });
}

function request(server, method, path, body) {
  return new Promise((resolve, reject) => {
    const addr = server.address();
    const req = http.request(
      {
        host: '127.0.0.1',
        port: addr.port,
        method,
        path,
        headers: { 'Content-Type': 'application/json' },
      },
      (res) => {
        let data = '';
        res.on('data', (c) => (data += c));
        res.on('end', () => {
          let json = null;
          try {
            json = JSON.parse(data);
          } catch {
            /* not JSON */
          }
          resolve({ status: res.statusCode, body: json });
        });
      }
    );
    req.on('error', reject);
    if (body !== undefined) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

const seed = [
  { prompt: '1/2 + 1/4', options: ['3/4'], answer: '3/4' },
  { prompt: 'reduce 4/8', options: ['1/2'], answer: '1/2' },
];

test('GET /play starts a game and returns a question', async () => {
  const { app } = createApp({ seedQuestions: seed });
  const server = await startServer(app);
  try {
    const res = await request(server, 'GET', '/play');
    assert.equal(res.status, 200);
    assert.equal(typeof res.body.gameId, 'number');
    assert.equal(res.body.totalQuestions, 2);
    assert.equal(res.body.firstQuestion.prompt, '1/2 + 1/4');
  } finally {
    server.close();
  }
});

test('full play-through returns a final score', async () => {
  const { app } = createApp({ seedQuestions: seed });
  const server = await startServer(app);
  try {
    const started = await request(server, 'GET', '/play');
    const gameId = started.body.gameId;
    await request(server, 'POST', `/games/${gameId}/answer`, { answer: '3/4' });
    const second = await request(server, 'POST', `/games/${gameId}/answer`, {
      answer: '1/4',
    });
    assert.equal(second.status, 200);
    assert.equal(second.body.gameOver, true);
    assert.deepEqual(second.body.score, { correct: 1, total: 2 });
  } finally {
    server.close();
  }
});

test('GET /games/:id/score returns score after game over', async () => {
  const { app } = createApp({ seedQuestions: seed });
  const server = await startServer(app);
  try {
    const started = await request(server, 'GET', '/play');
    const gameId = started.body.gameId;
    await request(server, 'POST', `/games/${gameId}/answer`, { answer: '3/4' });
    await request(server, 'POST', `/games/${gameId}/answer`, { answer: '1/2' });
    const res = await request(server, 'GET', `/games/${gameId}/score`);
    assert.equal(res.status, 200);
    assert.deepEqual(res.body.score, { correct: 2, total: 2 });
  } finally {
    server.close();
  }
});

test('POST /admin/questions validates and adds a question', async () => {
  const { app } = createApp({ seedQuestions: [] });
  const server = await startServer(app);
  try {
    const bad = await request(server, 'POST', '/admin/questions', { answer: '3/4' });
    assert.equal(bad.status, 400);

    const ok = await request(server, 'POST', '/admin/questions', {
      prompt: 'What is 1/3 + 1/3?',
      answer: '2/3',
      options: ['2/3', '1/6'],
    });
    assert.equal(ok.status, 201);
    assert.equal(ok.body.id, 1);
    assert.equal(ok.body.answer, '2/3');
  } finally {
    server.close();
  }
});

test('POST /admin/questions rejects invalid answer format', async () => {
  const { app } = createApp({ seedQuestions: [] });
  const server = await startServer(app);
  try {
    const res = await request(server, 'POST', '/admin/questions', {
      prompt: 'x',
      answer: '1/0',
    });
    assert.equal(res.status, 400);
  } finally {
    server.close();
  }
});

test('GET /help returns help text', async () => {
  const { app } = createApp({ seedQuestions: seed });
  const server = await startServer(app);
  try {
    const res = await request(server, 'GET', '/help');
    assert.equal(res.status, 200);
    assert.equal(typeof res.body.help, 'string');
  } finally {
    server.close();
  }
});

test('unknown game returns 404', async () => {
  const { app } = createApp({ seedQuestions: seed });
  const server = await startServer(app);
  try {
    const res = await request(server, 'GET', '/games/999/score');
    assert.equal(res.status, 404);
  } finally {
    server.close();
  }
});

test('pause/resume/gameover transitions return state', async () => {
  const { app } = createApp({ seedQuestions: seed });
  const server = await startServer(app);
  try {
    const started = await request(server, 'GET', '/play');
    const gameId = started.body.gameId;
    const paused = await request(server, 'POST', `/games/${gameId}/pause`);
    assert.equal(paused.body.state, 'Paused');
    const resumed = await request(server, 'POST', `/games/${gameId}/resume`);
    assert.equal(resumed.body.state, 'Playing');
    const over = await request(server, 'POST', `/games/${gameId}/gameover`);
    assert.equal(over.body.state, 'GameOver');
  } finally {
    server.close();
  }
});
