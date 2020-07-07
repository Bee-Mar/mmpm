import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { SelectionModel } from "@angular/cdk/collections";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";

@Component({
  selector: "app-installation-conflict-resolution-dialog",
  templateUrl: "./installation-conflict-resolution-dialog.component.html",
  styleUrls: ["./installation-conflict-resolution-dialog.component.scss"]
})
export class InstallationConflictResolutionDialogComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<InstallationConflictResolutionDialogComponent>,
    public dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  public selection: SelectionModel<any>;
  public disable: Array<boolean>;

  ngOnInit(): void {
    this.selection = new SelectionModel<any>(true, []);
    this.disable = new Array<boolean>(this.data?.matchesSelectedTitles?.length);
    this.disable.fill(false);
  }

  public onCancel(): void {
    if (this.data?.matchesSelectedTitles?.length) {
      const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
        data: {
          message: "The installation process will be cancelled"
        },
        disableClose: true
      });

      confirmationDialogRef.afterClosed().subscribe((yes) => {
        if (yes) {
          this.dialogRef.close();
        }
      });
    }
  }

  public onSubmit(): void {
    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: "The following will be installed"
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) this.dialogRef.close();

      for (const selected of this.selection.selected) {
        let index = this.data?.matchesSelectedTitles?.findIndex((pkg: MagicMirrorPackage) =>
          pkg.title === selected.value.title && pkg.author === selected.value.author && pkg.repository === selected.value.repository
        );

        this.data?.matchesSelectedTitles?.splice(index, 1);
      }

      this.dialogRef.close(this.data?.matchesSelectedTitles);
    });
  }

  public onSelection(pkg: any): void {
    this.selection.toggle(pkg);

    const allCanBeSelected = !this.selection.isSelected(pkg);
    let match: any;

    if (allCanBeSelected) {
      match = (p: MagicMirrorPackage) => p.title === pkg.value.title;
    } else {
      match = (p: MagicMirrorPackage) =>
        p.title === pkg.value.title && p.repository !== pkg.value.repository && p.author !== pkg.value.author;
    }

    for (const index in this.data?.matchesSelectedTitles) {
      if (match(this.data?.matchesSelectedTitles[index])) {
        // now allow a user to choose one of the available packages if this is
        // false, otherwise, one is already chosen
        this.disable[index] = !allCanBeSelected;
      }
    }
  }
}
