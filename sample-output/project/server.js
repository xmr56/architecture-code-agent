'use strict';

const { createApp } = require('./lib/app');

const PORT = process.env.PORT || 3000;

// Seed questions so the slice is usable out of the box.
const seedQuestions = [
  {
    category: 'fractions',
    prompt: 'What is 1/2 + 1/4? (answer in reduced form)',
    options: ['3/4', '2/6', '1/3', '3/8'],
    answer: '3/4',
  },
  {
    category: 'fractions',
    prompt: 'Reduce 4/8 to lowest terms.',
    options: ['1/2', '2/4', '4/8', '1/4'],
    answer: '1/2',
  },
  {
    category: 'fractions',
    prompt: 'What is 2/3 of 3? (write as whole number or fraction)',
    options: ['2', '6/3', '3/2', '1'],
    answer: '2',
  },
];

const { app } = createApp({ seedQuestions });

if (require.main === module) {
  app.listen(PORT, () => {
    // eslint-disable-next-line no-console
    console.log(`Space Fractions API listening on port ${PORT}`);
  });
}

module.exports = { app };
