import { Component, OnInit, Inject } from "@angular/core";
import {
  FormControl,
  FormGroupDirective,
  NgForm,
  Validators
} from "@angular/forms";
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA
} from "@angular/material/dialog";

@Component({
  selector: "app-external-module-source-registration",
  templateUrl: "./external-module-source-registration.component.html",
  styleUrls: ["./external-module-source-registration.component.scss"]
})
export class ExternalModuleSourceRegistrationComponent implements OnInit {
  title: string;
  author: string;
  repository: string;
  description: string;

  externalModuleFormControl = new FormControl("", [
    Validators.required,
    Validators.email
  ]);

  constructor(public dialog: MatDialog) {}

  openDialog(): void {
    const dialogRef = this.dialog.open(
      ExternalModuleSourceRegistrationComponent,
      {
        width: "250px",
        data: {
          title: this.title,
          author: this.author,
          repository: this.repository,
          description: this.description
        }
      }
    );

    dialogRef.afterClosed().subscribe((result) => {
      this.title = result;
    });
  }

  ngOnInit(): void {}
}
