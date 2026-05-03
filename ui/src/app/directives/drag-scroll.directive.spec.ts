import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DragScrollDirective } from './drag-scroll.directive';

@Component({
  standalone: false,
  template: `<div appDragScroll style="width:100px;overflow-x:auto;">
    <span style="display:inline-block;width:600px;height:10px;"></span>
  </div>`,
})
class TestHostComponent {}

describe('DragScrollDirective', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let el: HTMLElement;
  let directive: DragScrollDirective;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DragScrollDirective, TestHostComponent],
    });
    fixture = TestBed.createComponent(TestHostComponent);
    fixture.detectChanges();

    const debugEl = fixture.debugElement.query(By.directive(DragScrollDirective));
    el = debugEl.nativeElement;
    directive = debugEl.injector.get(DragScrollDirective);
  });

  afterEach(() => {
    // End any in-progress drag so tests don't bleed
    document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
  });

  it('should create', () => {
    expect(directive).toBeTruthy();
  });

  // ── mousedown ────────────────────────────────────────────────────────────

  describe('mousedown', () => {
    it('ignores non-left-button press', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 2, clientX: 50, bubbles: true }));
      expect((directive as any).dragging).toBeFalse();
      expect(el.style.cursor).toBe('');
    });

    it('starts drag on left-button press', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 100, bubbles: true }));
      expect((directive as any).dragging).toBeTrue();
    });

    it('records clientX as startX', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 75, bubbles: true }));
      expect((directive as any).startX).toBe(75);
    });

    it('records element scrollLeft as startScrollLeft', () => {
      let mockScrollLeft = 42;
      Object.defineProperty(el, 'scrollLeft', {
        get: () => mockScrollLeft,
        set: (v: number) => { mockScrollLeft = v; },
        configurable: true,
      });
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 100, bubbles: true }));
      expect((directive as any).startScrollLeft).toBe(42);
    });

    it('sets cursor to grabbing', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 50, bubbles: true }));
      expect(el.style.cursor).toBe('grabbing');
    });

    it('disables user-select', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 50, bubbles: true }));
      expect(el.style.userSelect).toBe('none');
    });

    it('resets moved flag on each new drag', () => {
      (directive as any).moved = true;
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 50, bubbles: true }));
      expect((directive as any).moved).toBeFalse();
    });
  });

  // ── document mousemove ───────────────────────────────────────────────────

  describe('document mousemove', () => {
    let mockScrollLeft: number;

    beforeEach(() => {
      mockScrollLeft = 0;
      Object.defineProperty(el, 'scrollLeft', {
        get: () => mockScrollLeft,
        set: (v: number) => { mockScrollLeft = v; },
        configurable: true,
      });
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 100, bubbles: true }));
    });

    it('does nothing when not dragging', () => {
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 50, bubbles: true }));
      expect(mockScrollLeft).toBe(0);
    });

    it('scrolls left when pointer moves right (dx positive)', () => {
      // startX=100, newX=120 → dx=20 → scrollLeft = 0 - 20 = -20 (clamped to 0 by browser)
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 120, bubbles: true }));
      expect(mockScrollLeft).toBe(-20);
    });

    it('scrolls right when pointer moves left (dx negative)', () => {
      // startX=100, newX=80 → dx=-20 → scrollLeft = 0 - (-20) = 20
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 80, bubbles: true }));
      expect(mockScrollLeft).toBe(20);
    });

    it('does not mark moved for displacement ≤ 4px', () => {
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 104, bubbles: true }));
      expect((directive as any).moved).toBeFalse();
    });

    it('marks moved for displacement > 4px', () => {
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 105, bubbles: true }));
      expect((directive as any).moved).toBeTrue();
    });
  });

  // ── document mouseup ─────────────────────────────────────────────────────

  describe('document mouseup', () => {
    beforeEach(() => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 50, bubbles: true }));
    });

    it('clears dragging flag', () => {
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      expect((directive as any).dragging).toBeFalse();
    });

    it('restores cursor', () => {
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      expect(el.style.cursor).toBe('');
    });

    it('restores user-select', () => {
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      expect(el.style.userSelect).toBe('');
    });
  });

  // ── click ────────────────────────────────────────────────────────────────

  describe('click', () => {
    it('suppresses click after drag exceeding 4px', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 100, bubbles: true }));
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 110, bubbles: true }));
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));

      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      spyOn(click, 'stopPropagation');
      spyOn(click, 'preventDefault');
      el.dispatchEvent(click);

      expect(click.stopPropagation).toHaveBeenCalled();
      expect(click.preventDefault).toHaveBeenCalled();
    });

    it('does not suppress click without prior drag', () => {
      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      spyOn(click, 'stopPropagation');
      spyOn(click, 'preventDefault');
      el.dispatchEvent(click);

      expect(click.stopPropagation).not.toHaveBeenCalled();
      expect(click.preventDefault).not.toHaveBeenCalled();
    });

    it('does not suppress click for displacement ≤ 4px', () => {
      el.dispatchEvent(new MouseEvent('mousedown', { button: 0, clientX: 100, bubbles: true }));
      document.dispatchEvent(new MouseEvent('mousemove', { clientX: 103, bubbles: true }));
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));

      const click = new MouseEvent('click', { bubbles: true, cancelable: true });
      spyOn(click, 'stopPropagation');
      spyOn(click, 'preventDefault');
      el.dispatchEvent(click);

      expect(click.stopPropagation).not.toHaveBeenCalled();
      expect(click.preventDefault).not.toHaveBeenCalled();
    });
  });
});
