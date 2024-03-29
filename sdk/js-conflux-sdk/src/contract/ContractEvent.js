const lodash = require('lodash');
const { assert, decorate } = require('../util');
const { EventCoder } = require('../abi');
const callable = require('../lib/callable');

class Event {
  constructor(cfx, eventLog, { address, topics }) {
    this.cfx = cfx;
    this.eventLog = eventLog;
    this.address = address;
    this.topics = topics;
  }

  getLogs(options = {}) {
    const _decodeLog = log => {
      if (log !== undefined) {
        log.params = this.eventLog.decodeLog(log);
      }
      return log;
    };

    // new LogIterator and decorate for decode params
    const iter = this.cfx.getLogs({
      ...options,
      address: this.address,
      topics: this.topics,
    });

    decorate(iter, 'next', async (func, args) => {
      return _decodeLog(await func(...args));
    });

    decorate(iter, 'then', (func, [resolve, reject]) => {
      return func(logs => resolve(logs.map(_decodeLog)), reject);
    });

    return iter;
  }
}

class ContractEvent {
  constructor(cfx, contract, name) {
    this.cfx = cfx;
    this.contract = contract;
    this.name = name;
    this.signatureToCoder = {};

    return callable(this, this.call.bind(this));
  }

  add(fragment) {
    const coder = new EventCoder(fragment);
    this.signatureToCoder[coder.signature()] = coder;
  }

  call(...args) {
    const matrix = [];
    const types = [];

    for (const [signature, coder] of Object.entries(this.signatureToCoder)) {
      if (!coder.anonymous) {
        try {
          matrix.push([signature, ...coder.encodeTopics(args)]);
        } catch (e) {
          types.push(coder.type);
        }
      }
    }

    if (!matrix.length) {
      throw new Error(`can not match "${types.join(',')}" with args (${args.join(',')})`);
    }

    // transpose matrix
    const topics = lodash.zip(...matrix).map(array => {
      array = array.filter(Boolean);
      return array.length ? array : null;
    });

    const address = this.contract.address;
    return new Event(this.cfx, this, { address, topics });
  }

  decodeLog(log) {
    const topic = log.topics[0];
    const coder = this.signatureToCoder[topic];

    assert(coder, {
      message: 'ContractEvent.decodeLog topic missing',
      expect: topic,
      got: Object.keys(this.signatureToCoder),
      coder: this,
    });

    const namedTuple = coder.decodeLog(log);
    return {
      name: this.name,
      fullName: coder.fullName,
      type: coder.type,
      signature: topic,
      array: [...namedTuple],
      object: namedTuple.toObject(),
    };
  }
}

ContractEvent.Event = Event;

module.exports = ContractEvent;
