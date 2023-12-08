export class RingBuffer<T> {
  private buffer: Array<T>;
  private capacity = 0;
  private size = 0;
  private head = 0;
  private tail = 0;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.buffer = new Array<T>(this.capacity);
  }

  public push(item: T): void {
    this.buffer[this.tail] = item;
    this.tail = this.next_index(this.tail);

    if (this.full()) {
      this.head = this.next_index(this.head);
    } else {
      this.size++;
    }
  }

  private next_index(current: number): number {
    return (current + 1) % this.capacity;
  }

  public empty(): boolean {
    return this.size === 0;
  }

  public full(): boolean {
    return this.size === this.capacity;
  }

  // so it can be looped over
  [Symbol.iterator](): Iterator<T> {
    let index = this.head;
    let count = 0;

    return {
      next: () => {
        if (count < this.size) {
          const value = this.buffer[index];
          index = this.next_index(index);
          count++;
          return {value, done: false};
        } else {
          return {value: null, done: true};
        }
      }
    };
  }
}
