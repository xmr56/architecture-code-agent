'use strict';

// Question entity + repository. In-memory implementation for the executable slice.
// A PostgreSQL-backed implementation can satisfy the same interface (see sql/game_ddl.sql).

class QuestionRepository {
  constructor(initialQuestions = []) {
    this.items = new Map();
    this.nextId = 1;
    for (const q of initialQuestions) {
      this.add(q);
    }
  }

  add({ category, prompt, options, answer }) {
    const id = this.nextId++;
    const question = {
      id,
      category: category || 'fractions',
      prompt,
      options: Array.isArray(options) ? options.slice() : [],
      answer, // reduced string form "a/b" (authoritative answer key)
    };
    this.items.set(id, question);
    return question;
  }

  get(id) {
    const q = this.items.get(id);
    return q ? { ...q, options: q.options.slice() } : null;
  }

  list() {
    return [...this.items.values()].map((q) => ({
      ...q,
      options: q.options.slice(),
    }));
  }

  count() {
    return this.items.size;
  }
}

module.exports = { QuestionRepository };
