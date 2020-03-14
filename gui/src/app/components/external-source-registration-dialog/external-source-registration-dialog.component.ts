import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { FormControl, Validators } from "@angular/forms";

@Component({
  selector: "app-external-source-registration-dialog",
  templateUrl: "./external-source-registration-dialog.component.html",
  styleUrls: ["./external-source-registration-dialog.component.scss"]
})
export class ExternalSourceRegistrationDialogComponent implements OnInit {
  title: string = "";
  repository: string = "";
  author: string = "";
  description: string = "";

  externalSource: MagicMirrorPackage;

  titleFormControl = new FormControl("", [Validators.required]);
  repositoryFormControl = new FormControl("", [Validators.required]);
  authorFormControl = new FormControl("", [Validators.required]);
  descriptionFormControl = new FormControl("", [Validators.required]);

  constructor(
    private dialogRef: MatDialogRef<ExternalSourceRegistrationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {
    this.externalSource = this.data.externalSource;
    console.log(this.data.externalSources);
  }

  public getErrorMessage(formControl: FormControl): string {
    if (formControl.hasError("required")) {
      return "You must enter a value";
    }
  }

  public onRegisterSource(): void {
    if (
      this.externalSource.title &&
      this.externalSource.repository &&
      this.externalSource.author &&
      this.externalSource.description
    ) {
      this.dialogRef.close(this.externalSource);
    }
  }

  public onNoClick(): void {
    this.dialogRef.close();
  }
}
