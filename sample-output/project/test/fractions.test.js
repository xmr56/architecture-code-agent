'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { gcd, reduce, parseFraction, equalFraction } = require('../lib/fractions');

test('gcd computes greatest common divisor', () => {
  assert.equal(gcd(4, 8), 4);
  assert.equal(gcd(7, 3), 1);
  assert.equal(gcd(0, 5), 5);
});

test('reduce normalizes signs and simplifies', () => {
  assert.deepEqual(reduce(4, 8), { n: 1, d: 2 });
  assert.deepEqual(reduce(-2, -4), { n: 1, d: 2 });
  assert.deepEqual(reduce(2, -4), { n: -1, d: 2 });
  assert.deepEqual(reduce(0, 7), { n: 0, d: 1 });
});

test('parseFraction parses fraction and whole-number strings', () => {
  assert.deepEqual(parseFraction('3/4'), { n: 3, d: 4 });
  assert.deepEqual(parseFraction('2'), { n: 2, d: 1 });
  assert.deepEqual(parseFraction('-2/5'), { n: -2, d: 5 });
  assert.deepEqual(parseFraction('4/8'), { n: 1, d: 2 });
});

test('parseFraction rejects invalid input', () => {
  assert.equal(parseFraction(''), null);
  assert.equal(parseFraction('abc'), null);
  assert.equal(parseFraction('1/0'), null);
  assert.equal(parseFraction(null), null);
  assert.equal(parseFraction(123), null);
});

test('equalFraction compares reduced fractions', () => {
  assert.equal(equalFraction({ n: 1, d: 2 }, { n: 2, d: 4 }), false); // reduced forms differ
  assert.equal(equalFraction(parseFraction('1/2'), parseFraction('2/4')), true);
  assert.equal(equalFraction(parseFraction('2'), parseFraction('4/2')), true);
});
