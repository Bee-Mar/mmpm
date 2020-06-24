import { Component, OnInit } from "@angular/core";
import { MatDialogRef } from "@angular/material/dialog";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { FormControl, Validators } from "@angular/forms";

@Component({
  selector: "app-external-source-registration-dialog",
  templateUrl: "./external-source-registration-dialog.component.html",
  styleUrls: ["./external-source-registration-dialog.component.scss"]
})
export class ExternalSourceRegistrationDialogComponent implements OnInit {
  public title: string = "";
  public repository: string = "";
  public author: string = "";
  public description: string = "";

  public titleFormControl = new FormControl("", [Validators.required]);
  public repositoryFormControl = new FormControl("", [Validators.required]);
  public authorFormControl = new FormControl("", [Validators.required]);
  public descriptionFormControl = new FormControl("", [Validators.required]);

  constructor(
    private dialogRef: MatDialogRef<ExternalSourceRegistrationDialogComponent>,
  ) {}

  ngOnInit(): void {}

  public getErrorMessage(formControl: FormControl): string {
    if (formControl.hasError("required")) {
      return "You must enter a value";
    }
  }

  public onRegisterSource(): void {
    if (this.title && this.repository && this.author && this.description) {
      const pkg: MagicMirrorPackage = {
        title: this.title,
        repository: this.repository,
        author: this.author,
        description: this.description,
        category: "External Module Sources",
        directory: "",
      };

      this.dialogRef.close(pkg);
    }
  }

  public onNoClick(): void {
    this.dialogRef.close();
  }
}
