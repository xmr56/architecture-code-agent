'use strict';

// Fraction arithmetic helpers used for answer grading.
//
// A fraction is represented as { n: number, d: number } with d > 0 and gcd(n, d) == 1
// (reduced form). Supports parsing of "a/b" and plain integers/decimals-as-strings
// are treated as integers (the slice only deals in fractions and whole numbers).

function gcd(a, b) {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b) {
    const t = b;
    b = a % b;
    a = t;
  }
  return a === 0 ? 1 : a;
}

function reduce(n, d) {
  if (d === 0) {
    throw new Error('denominator must not be zero');
  }
  if (d < 0) {
    n = -n;
    d = -d;
  }
  const g = gcd(n, d);
  return { n: n / g, d: d / g };
}

// Parse a string like "3/4", "-2/5", or "7" into a reduced fraction.
// Returns null on invalid input.
function parseFraction(input) {
  if (typeof input !== 'string') {
    return null;
  }
  const s = input.trim();
  if (s === '') {
    return null;
  }
  const m = s.match(/^(-?\d+)(?:\/(-?\d+))?$/);
  if (!m) {
    return null;
  }
  const n = parseInt(m[1], 10);
  if (m[2] === undefined) {
    return reduce(n, 1);
  }
  const d = parseInt(m[2], 10);
  if (d === 0) {
    return null;
  }
  return reduce(n, d);
}

function equalFraction(a, b) {
  return a.n === b.n && a.d === b.d;
}

module.exports = { gcd, reduce, parseFraction, equalFraction };
