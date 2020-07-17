import { Component, OnInit } from '@angular/core';
import { MatDialog } from "@angular/material/dialog";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { AvailableUpgradesModalDialogComponent } from "src/app/components/available-upgrades-modal-dialog/available-upgrades-modal-dialog.component";

@Component({
  selector: 'app-available-upgrades-ticker',
  templateUrl: './available-upgrades-ticker.component.html',
  styleUrls: ['./available-upgrades-ticker.component.scss']
})
export class AvailableUpgradesTickerComponent implements OnInit {

  constructor(
    private dataStore: DataStoreService,
    public dialog: MatDialog,
  ) {}

  public availableUpgrades: Array<MagicMirrorPackage>;
  public count: number;

  public ngOnInit(): void {
    this.dataStore.upgradeablePackages.subscribe((upgradeable) => {
      this.availableUpgrades = upgradeable;
      this.count = upgradeable?.packages?.length + Number(upgradeable?.MagicMirror);
    });
  }

  public showAvailableUpgrades(): void {
    this.dialog.open(AvailableUpgradesModalDialogComponent, {
      height: "60vh",
      width: "40vw",
      disableClose: true
    });
  }
}
