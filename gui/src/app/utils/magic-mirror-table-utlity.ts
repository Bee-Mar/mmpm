import { MatSort } from "@angular/material/sort";
import { MatDialog } from "@angular/material/dialog";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { PackageDetailsModalComponent } from "src/app/components/package-details-modal/package-details-modal.component";
import { TooltipPosition } from "@angular/material/tooltip";

export class MagicMirrorTableUtility {
  constructor(
    private selection: SelectionModel<MagicMirrorPackage>,
    private dataSource: MatTableDataSource<MagicMirrorPackage>,
    private sort: MatSort,
    public dialog: MatDialog,
  ) {}

  public displayedColumns: string[] = [
    "select",
    "category",
    "title",
    "description"
  ];

  public tooltipPosition: TooltipPosition[] = ["below"];

  public setTooltipPosition(position: any): void {
    this.tooltipPosition = [position];
  }

  public compare(a: number | string, b: number | string, ascending: boolean): number {
    return (a < b ? -1 : 1) * (ascending ? 1 : -1);
  }

  public onSort(event: Event, packages: MagicMirrorPackage[]): MagicMirrorPackage[] {
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

  public isAllSelected(data?: Array<MagicMirrorPackage>): boolean {
    if (!data) {
      return this.dataSource?.data?.length === this.selection.selected.length;
    }

    return data?.length === this.selection.selected.length;
  }

  public toggleSelectAll(): void {
    if (this.dataSource?.filteredData?.length) {
      this.isAllSelected(this.dataSource?.filteredData) ?
        this.selection.clear() : this.dataSource?.filteredData.forEach((row) => this.selection.select(row));
      return;
    }

    this.isAllSelected(this.dataSource.data) ?
    this.selection.clear() : this.dataSource?.data.forEach((row) => this.selection.select(row));
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) return `${this.isAllSelected(this.dataSource?.data) ? "select" : "deselect"} all`;
    return `${this.selection.isSelected(row) ? "deselect" : "select"} row ${row.category + 1}`;
  }

  public trimDescription(description: string): string {
    const maxDescriptionLength: number = 75;

    if (description.length <= maxDescriptionLength)
      return description;

    return `${description.slice(0, maxDescriptionLength - 3)} ...`;
  }

  public showPackageDetails(pkg: MagicMirrorPackage) {
    // since clicking on a cell selects the value, this actually sets the value
    // to state it was in at the time of selection
    this.selection.toggle(pkg);

    this.dialog.open(PackageDetailsModalComponent, {
      width: "45vw",
      height: "60vh",
      disableClose: true,
      data: pkg
    });
  }

  public clearFilter(): void {
    this.dataSource.filter = "";
    let el = document.getElementById("searchbar") as HTMLInputElement;
    el.value = "";
  }
}

