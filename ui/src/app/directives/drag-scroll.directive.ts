import { Directive, ElementRef, HostListener, inject } from '@angular/core';

@Directive({ selector: '[appDragScroll]', standalone: false })
export class DragScrollDirective {
  private el = inject(ElementRef<HTMLElement>);

  private dragging = false;
  private startX = 0;
  private startScrollLeft = 0;
  private moved = false;

  @HostListener('mousedown', ['$event'])
  onMouseDown(e: MouseEvent): void {
    if (e.button !== 0) return;
    this.dragging = true;
    this.moved = false;
    this.startX = e.clientX;
    this.startScrollLeft = this.el.nativeElement.scrollLeft;
    this.el.nativeElement.style.cursor = 'grabbing';
    this.el.nativeElement.style.userSelect = 'none';
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(e: MouseEvent): void {
    if (!this.dragging) return;
    const dx = e.clientX - this.startX;
    if (Math.abs(dx) > 4) this.moved = true;
    this.el.nativeElement.scrollLeft = this.startScrollLeft - dx;
  }

  @HostListener('document:mouseup')
  onMouseUp(): void {
    this.dragging = false;
    this.el.nativeElement.style.cursor = '';
    this.el.nativeElement.style.userSelect = '';
  }

  @HostListener('click', ['$event'])
  onClick(e: MouseEvent): void {
    if (this.moved) {
      e.stopPropagation();
      e.preventDefault();
    }
  }
}
