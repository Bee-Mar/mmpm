import { MagicMirrorPackage, RemotePackageDetails } from "@/models/magicmirror-package";
import { Component, Input, Output, EventEmitter } from "@angular/core";
import { MarketPlaceIcons } from "@/components/marketplace/marketplace-icons.model";
import { APIResponse } from "@/services/api/base-api";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { MessageService } from "primeng/api";
import assert from "assert";

@Component({
  selector: "app-package-details-viewer",
  templateUrl: "./package-details-viewer.component.html",
  styleUrls: ["./package-details-viewer.component.scss"],
  providers: [MessageService],
  standalone: false,
})
export class PackageDetailsViewerComponent {
  constructor(
    private mmPkgApi: MagicMirrorPackageAPI,
    private msg: MessageService,
  ) {}

  @Input()
  public display: boolean;

  @Output()
  public displayChange = new EventEmitter<boolean>();

  @Input()
  public selectedPackage: MagicMirrorPackage | null;

  @Output()
  public selectedPackageChange = new EventEmitter<MagicMirrorPackage | null>();

  public loading = false;
  public icons = MarketPlaceIcons;

  public onHideDisplay(): void {
    this.selectedPackageChange.emit(null);
    this.displayChange.emit(false);
  }

  public getPackageDetails(): void {
    if (this.selectedPackage === null) {
      return;
    }

    if (typeof this.selectedPackage?.remote_details != "undefined") {
      console.log(`${this.selectedPackage?.title} already has remote_details stored`);
      this.loading = false;
      return;
    }

    this.loading = true;
    console.log(`${this.selectedPackage?.title} does not have remote_details stored. Collecting...`);

    this.mmPkgApi
      .postDetails(this.selectedPackage)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.selectedPackage!.remote_details = response.message as RemotePackageDetails;

          console.log(`Retrieved remote details for ${this.selectedPackage?.title}`);
          this.loading = false;
        } else {
          this.msg.add({
            severity: "error",
            summary: "Package Details",
            detail: response.message,
          });
        }
      })
      .catch((error) => {
        console.log(error);
        // failed getting remote details (probably because we exceeded the request count)
        // so we need to still display some content
        this.loading = false;
      });
  }
}
