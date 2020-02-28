import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators
} from "@angular/forms";

export interface MagicMirrorPackage {
  title: string;
  category: string;
  repository: string;
  author: string;
  description: string;
}

let PACKAGES: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
let SORTED_PACKAGES: Array<MagicMirrorPackage> = new Array<
  MagicMirrorPackage
>();

@Component({
  selector: "app-external-source-registration-form",
  templateUrl: "./external-source-registration-form.component.html",
  styleUrls: ["./external-source-registration-form.component.scss"]
})
export class ExternalSourceRegistrationFormComponent implements OnInit {
  title = new FormControl("", [Validators.required]);
  repository = new FormControl("", [Validators.required]);
  author = new FormControl("", [Validators.required]);
  description = new FormControl("", [Validators.required]);

  constructor(private api: RestApiService) {}

  ngOnInit(): void {

    this.api.mmpmApiRequest("/external-module-sources").subscribe((packages) => {
      Object.keys(packages).forEach((category) => {
        for (let pkg of packages[category]) {
          PACKAGES.push({
            category: category,
            title: pkg["Title"],
            description: pkg["Description"],
            author: pkg["Author"],
            repository: pkg["Repository"]
          });
        }
      });
    });
  }

  public getErrorMessage(): string {
    if (this.title.hasError("required")) {
      return "You must enter a value";
    }

    return this.title.hasError("title") ? "Not a valid title" : "";
  }

  public registerExternalModuleSource(): void {
    if (this.title && this.repository && this.author && this.description) {
      this.api.mmpmApiRequest("/register-external-module-source").subscribe((response) => {
        console.log(response);
      });
    }
  }
}
