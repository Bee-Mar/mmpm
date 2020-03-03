import { Component, OnInit, Inject } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators
} from "@angular/forms";

import { MatDialogRef } from "@angular/material/dialog";

export interface MagicMirrorPackage {
  title: string;
  category: string;
  repository: string;
  author: string;
  description: string;
}

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

  titleFormControl = new FormControl("", [Validators.required]);
  repositoryFormControl = new FormControl("", [Validators.required]);
  authorFormControl = new FormControl("", [Validators.required]);
  descriptionFormControl = new FormControl("", [Validators.required]);

  constructor(
    public api: RestApiService,
    public dialogRef: MatDialogRef<ExternalSourceRegistrationDialogComponent>
  ) {}

  ngOnInit(): void {}

  public getErrorMessage(): string {
    if (this.titleFormControl.hasError("required")) {
      return "You must enter a value";
    }

    return this.titleFormControl.hasError("title") ? "Not a valid title" : "";
  }

  public registerExternalModuleSource(): void {
    if (this.title && this.repository && this.author && this.description) {
      this.api
        .mmpmApiRequest("/register-external-module-source")
        .subscribe((response) => {
          console.log(response);
        });
    }
  }

  public onNoClick(): void {
    this.dialogRef.close();
  }
}
