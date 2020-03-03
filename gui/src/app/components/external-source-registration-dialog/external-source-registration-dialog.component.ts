import { Component, OnInit, Inject } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators
} from "@angular/forms";

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
  }

  public getErrorMessage(): string {
    if (this.titleFormControl.hasError("required")) {
      return "You must enter a value";
    }

    return this.titleFormControl.hasError("title") ? "Not a valid title" : "";
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
