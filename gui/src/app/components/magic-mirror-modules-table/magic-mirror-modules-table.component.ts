import { Component, ViewChild, Input } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator } from "@angular/material/paginator";
import { ExternalSourceRegistrationDialogComponent } from "src/app/components/external-source-registration-dialog/external-source-registration-dialog.component";

import {MatDialog, MatDialogRef, MAT_DIALOG_DATA} from '@angular/material/dialog';

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
  selector: "app-magic-mirror-modules-table",
  styleUrls: ["./magic-mirror-modules-table.component.scss"],
  templateUrl: "./magic-mirror-modules-table.component.html"
})
export class MagicMirrorModulesTableComponent {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  @Input() url: string;

  constructor(
    private api: RestApiService,
    public dialog: MatDialog
  ) {}

  displayedColumns: string[] = [
    "select",
    "category",
    "title",
    "repository",
    "author",
    "description"
  ];

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);

  public ngOnInit(): void {
    this.paginator.pageSize = 10;

    this.api.mmpmApiRequest(`/${this.url}`).subscribe((packages) => {
      Object.keys(packages).forEach((category) => {
        if (packages) {
          for (const pkg of packages[category]) {
            PACKAGES.push({
              category,
              title: pkg["Title"],
              description: pkg["Description"],
              author: pkg["Author"],
              repository: pkg["Repository"]
            });
          }
        }
      });

      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(PACKAGES);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }

  public compare(a: number | string, b: number | string, ascending: boolean) {
    return (a < b ? -1 : 1) * (ascending ? 1 : -1);
  }

  public onSort(sort: MatSort) {
    const data = PACKAGES.slice();

    if (!sort.active || sort.direction === "") {
      SORTED_PACKAGES = data;
      return;
    }

    SORTED_PACKAGES = data.sort((a, b) => {
      const ascending = sort.direction === "asc";
      switch (sort.active) {
        case "category":
          return this.compare(a.category, b.category, ascending);
        case "title":
          return this.compare(a.title, b.title, ascending);
        case "author":
          return this.compare(a.author, b.author, ascending);
        default:
          return 0;
      }
    });

    PACKAGES = SORTED_PACKAGES;
  }

  public searchFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  public isAllSelected(): boolean {
    return this.dataSource?.data.length === this.selection.selected.length;
  }

  public toggleSelectAll(): void {
    this.isAllSelected()
      ? this.selection.clear()
      : this.dataSource?.data.forEach((row) => this.selection.select(row));
  }

  public onInstallModules(): void {
    if (this.selection.selected.length) {
      this.api
        .installSelectedModules(this.selection.selected)
        .subscribe((result) => {
          console.log(result);
        });
    }
  }

  public onAddExternalSource(): void {
    const dialogRef = this.dialog.open(ExternalSourceRegistrationDialogComponent, {
      width: "50vw",
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log("The dialog was closed");
    });
  }

  public onRemoveModules(): void {}

  public onUpdateModules(): void {}

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) {
      return `${this.isAllSelected() ? "select" : "deselect"} all`;
    }

    return `${
      this.selection.isSelected(row) ? "deselect" : "select"
    } row ${row.category + 1}`;
  }
}
