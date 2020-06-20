import { MatSort } from "@angular/material/sort";
import { MatDialog } from "@angular/material/dialog";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { ModuleDetailsModalComponent } from "src/app/components/module-details-modal/module-details-modal.component";

export class MagicMirrorTableUtility {

  constructor(
    private selection: SelectionModel<MagicMirrorPackage>,
    private dataSource: MatTableDataSource<MagicMirrorPackage>,
    private sort: MatSort,
    public dialog: MatDialog
  ) {}


  public compare(a: number | string, b: number | string, ascending: boolean): number {
    return (a < b ? -1 : 1) * (ascending ? 1 : -1);
  }

  public onSort(event: Event, packages: MagicMirrorPackage[]) {
    const data = packages.slice();

    if (!this.sort.active || this.sort.direction === "") {
      packages = data;
    } else {
      packages = data.sort((a: MagicMirrorPackage, b: MagicMirrorPackage) => {
        const ascending = this.sort.direction === "asc";

        switch (this.sort.active) {
          case "category":
            return this.compare(a.category, b.category, ascending);
          case "title":
            return this.compare(a.title, b.title, ascending);
          default:
            return 0;
        }
      });
    }

    return packages;
  }

  public searchFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  public isAllSelected(): boolean {
    return this.dataSource?.data.length === this.selection.selected.length;
  }

  public toggleSelectAll(): void {
    this.isAllSelected() ? this.selection.clear() : this.dataSource?.data.forEach((row) => { this.selection.select(row); });
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) return `${this.isAllSelected() ? "select" : "deselect"} all`;
    return `${this.selection.isSelected(row) ? "deselect" : "select"} row ${row.category + 1}`;
  }

  public showModuleDetails(pkg: MagicMirrorPackage) {
    // since clicking on a cell selects the value, this actually sets the value
    // to state it was in at the time of selection
    this.selection.toggle(pkg);

    this.dialog.open(ModuleDetailsModalComponent, {
      width: "45vw",
      height: "50vh",
      disableClose: true,
      data: pkg
    });
  }
}


export function fillMagicMirrorPackageArray(data: object) {
  let array: MagicMirrorPackage[] = new Array<MagicMirrorPackage>();

  Object.keys(data).forEach((_category) => {
    if (data) {
      for (const pkg of data[_category]) {
        array.push({
          category: _category,
          title: pkg["title"],
          description: pkg["description"],
          author: pkg["author"],
          repository: pkg["repository"],
          directory: pkg["directory"] ?? ""
        });
      }
    }
  });

  return array;
}


