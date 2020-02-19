import { Component, ViewChild } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { Sort } from "@angular/material/sort";
import { MatPaginator } from "@angular/material/paginator";

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

  constructor(private api: RestApiService) {}

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

  ngOnInit() {
    this.api.mmpmApiRequest("/modules").subscribe((packages) => {
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

      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(PACKAGES);
      this.dataSource.paginator = this.paginator;
    });
  }

  public compare(a: number | string, b: number | string, isAsc: boolean) {
    return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
  }

  public sort(sort: Sort) {
    const data = PACKAGES.slice();
    if (!sort.active || sort.direction === "") {
      SORTED_PACKAGES = data;
      return;
    }

    SORTED_PACKAGES = data.sort((a, b) => {
      const isAsc = sort.direction === "asc";
      switch (sort.active) {
        case "category":
          return this.compare(a.category, b.category, isAsc);
        case "title":
          return this.compare(a.title, b.title, isAsc);
        case "author":
          return this.compare(a.author, b.author, isAsc);
        default:
          return 0;
      }
    });

    PACKAGES = SORTED_PACKAGES;
    this.dataSource = new MatTableDataSource<MagicMirrorPackage>(PACKAGES);
  }

  public searchFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  public isAllSelected(): boolean {
    return this.dataSource?.data.length == this.selection.selected.length;
  }

  public toggleSelectAll(): void {
    this.isAllSelected()
      ? this.selection.clear()
      : this.dataSource?.data.forEach((row) => this.selection.select(row));
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) return `${this.isAllSelected() ? "select" : "deselect"} all`;
    return `${
      this.selection.isSelected(row) ? "deselect" : "select"
    } row ${row.category + 1}`;
  }
}
