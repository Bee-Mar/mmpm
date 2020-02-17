import { Component } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";

export interface MagicMirrorPackage {
  name: string;
  position: number;
  weight: number;
  symbol: string;
}

const ELEMENT_DATA: MagicMirrorPackage[] = [
  { position: 1, name: "Hydrogen", weight: 1.0079, symbol: "H" },
  { position: 2, name: "Helium", weight: 4.0026, symbol: "He" },
  { position: 3, name: "Lithium", weight: 6.941, symbol: "Li" },
  { position: 4, name: "Beryllium", weight: 9.0122, symbol: "Be" },
  { position: 5, name: "Boron", weight: 10.811, symbol: "B" },
  { position: 6, name: "Carbon", weight: 12.0107, symbol: "C" },
  { position: 7, name: "Nitrogen", weight: 14.0067, symbol: "N" },
  { position: 8, name: "Oxygen", weight: 15.9994, symbol: "O" },
  { position: 9, name: "Fluorine", weight: 18.9984, symbol: "F" },
  { position: 10, name: "Neon", weight: 20.1797, symbol: "Ne" }
];

@Component({
  selector: "app-magic-mirror-modules-table",
  styleUrls: ["./magic-mirror-modules-table.component.scss"],
  templateUrl: "./magic-mirror-modules-table.component.html"
})
export class MagicMirrorModulesTableComponent {
  displayedColumns: string[] = [
    "select",
    "position",
    "name",
    "weight",
    "symbol"
  ];
  dataSource = new MatTableDataSource<MagicMirrorPackage>(ELEMENT_DATA);
  selection = new SelectionModel<MagicMirrorPackage>(true, []);

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  public isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.dataSource.data.length;
    return numSelected === numRows;
  }

  public masterToggle(): void {
    this.isAllSelected()
      ? this.selection.clear()
      : this.dataSource.data.forEach((row) => this.selection.select(row));
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) {
      return `${this.isAllSelected() ? "select" : "deselect"} all`;
    }
    return `${
      this.selection.isSelected(row) ? "deselect" : "select"
    } row ${row.position + 1}`;
  }
}
