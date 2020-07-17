import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from "@angular/material/dialog";
import { FormControl } from '@angular/forms';

@Component({
  selector: 'app-select-modal',
  templateUrl: './select-modal.component.html',
  styleUrls: ['./select-modal.component.scss']
})
export class SelectModalComponent implements OnInit {

  constructor(
    private dialogRef: MatDialogRef<SelectModalComponent>,
    public dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) public data: any

  ) {}

  public selected: number = 0;
  public choicesFormControl = new FormControl();

  ngOnInit(): void {
  }

  public onConfirm(choice: any): void {
    this.dialogRef.close(choice);
  }
}
