import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: 'app-available-upgrades-modal-dialog',
  templateUrl: './available-upgrades-modal-dialog.component.html',
  styleUrls: ['./available-upgrades-modal-dialog.component.scss']
})
export class AvailableUpgradesModalDialogComponent implements OnInit {

  constructor(
    private dialogRef: MatDialogRef<AvailableUpgradesModalDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  ngOnInit(): void {
    console.log(this.data);
  }

}
