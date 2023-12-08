import {RingBuffer} from './ring-buffer';

describe('RingBuffer', () => {
  it('should create an instance', () => {
    expect(new RingBuffer(10)).toBeTruthy();
  });
});
