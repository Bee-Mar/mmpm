import { Component, OnInit, Inject } from "@angular/core";
import {  MAT_DIALOG_DATA } from "@angular/material/dialog";
import { RestApiService } from "src/app/services/rest-api.service";
import { MMPMUtility } from "src/app/utils/mmpm-utility";

@Component({
  selector: "app-package-details-modal",
  templateUrl: "./package-details-modal.component.html",
  styleUrls: ["./package-details-modal.component.scss"]
})
export class PackageDetailsModalComponent implements OnInit {

  constructor(
    private api: RestApiService,
    public mmpmUtility: MMPMUtility,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }


  public ngOnInit(): void {
    this.api.getRepoDetails([this.data]).then((response: any) => {
      response = JSON.parse(response);

      if (response.length)
        this.data = {...this.data, ...response[0].details};
    }).catch((error) => console.log(error));
  }

  public onNoClick(): void {}
}
