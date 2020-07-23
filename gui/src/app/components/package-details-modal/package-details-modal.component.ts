import { Component, OnInit, Inject } from "@angular/core";
import { MAT_DIALOG_DATA } from "@angular/material/dialog";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";

@Component({
  selector: "app-package-details-modal",
  templateUrl: "./package-details-modal.component.html",
  styleUrls: ["./package-details-modal.component.scss"]
})
export class PackageDetailsModalComponent implements OnInit {

  constructor(
    private mSnackBar: MatSnackBar,
    public mmpmUtility: MMPMUtility,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);

  // this shouldn't have to be duplicated from mmpm.utils, but since the requests library and
  // greenlet don't play nicely, I have no choice at the moment. Green threads ... wtf
  public ngOnInit(): void {
    const pkg: MagicMirrorPackage = this.data;
    const split: Array<string> = pkg.repository.split("/");
    const user: string = split[split.length - 2];
    const project: string = split[split.length - 1].replace(".git", ""); // in case the user added .git at the end
    const url: string = pkg.repository.toLowerCase();

    if (url.includes("github")) {
      let api: string = `https://api.github.com/repos/${user}/${project}`

      fetch(api).then((response) => response.json()).then((gitHubData) => {

        this.data = {
          ...this.data,
          stars: gitHubData["stargazers_count"] ?? "N/A",
          issues: gitHubData["open_issues"] ?? "N/A",
          created: gitHubData["created_at"]?.split("T")[0] ?? "N/A",
          updated: gitHubData["updated_at"]?.split("T")[0] ?? "N/A",
          forks: gitHubData["forks_count"] ?? "N/A"
        };

      }).catch((error) => console.log(error));

    } else if (url.includes("gitlab")) {
      let api: string = `https://gitlab.com/api/v4/projects/${user}%2F${project}`;

      fetch(api).then((response) => response.json()).then((gitlabData) => {
        fetch(`${api}/issues`).then((response) => response.json()).then((issues) => {
          this.data = {
            ...this.data,
            stars: gitlabData["star_count"] ?? "N/A",
            issues: issues?.length ?? "N/A",
            created: gitlabData["created_at"]?.split("T")[0] ?? "N/A",
            updated: gitlabData["last_activity_at"]?.split("T")[0] ?? "N/A",
            forks: gitlabData["forks_count"] ?? "N/A"
          };
        }).catch((error) => console.log(error));
      }).catch((error) => console.log(error));

    } else if (url.includes("bitbucket")) {
      let api: string = `https://api.bitbucket.org/2.0/repositories/${user}/${project}`;

      fetch(api).then((response) => response.json()).then((bitbucketData) => {
        fetch(`${api}/watchers`).then((response) => response.json()).then((watchers) => {
          fetch(`${api}/forks`).then((response) => response.json()).then((forks) => {
            fetch(`${api}/issues`).then((response) => response.json()).then((issues) => {

              this.data = {
                ...this.data,
                stars: watchers["pagelen"] ?? "N/A",
                issues: issues["pagelen"] ?? "N/A",
                created: bitbucketData["created_on"]?.split("T")[0] ?? "N/A",
                updated: bitbucketData["updated_on"]?.split("T")[0] ?? "N/A",
                forks: forks["pagelen"] ?? "N/A"
              }

            }).catch((error) => console.log(error));
          }).catch((error) => console.log(error));
        }).catch((error) => console.log(error));
      }).catch((error) => console.log(error));
    }
  }

  public onNoClick(): void { }
}
