import { Component } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";

export interface MMPackage {
  title: string;
  category: number;
  repository: number;
  author: string;
  description: string;
}

const PACKAGES: MMPackage[] = [
  {
    category: 1,
    title: "Hydrogen",
    repository: 1.0079,
    author: "H",
    description: "Desc"
  },
  {
    category: 2,
    title: "Helium",
    repository: 4.0026,
    author: "He",
    description: "Desc"
  },
  {
    category: 3,
    title: "Lithium",
    repository: 6.941,
    author: "Li",
    description: "Desc"
  },
  {
    category: 4,
    title: "Beryllium",
    repository: 9.0122,
    author: "Be",
    description: "Desc"
  },
  {
    category: 5,
    title: "Boron",
    repository: 10.811,
    author: "B",
    description: "Desc"
  },
  {
    category: 6,
    title: "Carbon",
    repository: 12.0107,
    author: "C",
    description: "Desc"
  },
  {
    category: 7,
    title: "Nitrogen",
    repository: 14.0067,
    author: "N",
    description: "Desc"
  },
  {
    category: 8,
    title: "Oxygen",
    repository: 15.9994,
    author: "O",
    description: "Desc"
  },
  {
    category: 9,
    title: "Fluorine",
    repository: 18.9984,
    author: "F",
    description: "Desc"
  },
  {
    category: 10,
    title: "Neon",
    repository: 20.1797,
    author: "Ne",
    description: "Desc"
  }
];

@Component({
  selector: "app-magic-mirror-modules-table",
  styleUrls: ["./magic-mirror-modules-table.component.scss"],
  templateUrl: "./magic-mirror-modules-table.component.html"
})
export class MagicMirrorModulesTableComponent {
  constructor(private api: RestApiService) {}

  displayedColumns: string[] = [
    "select",
    "category",
    "title",
    "repository",
    "author",
    "description"
  ];

  dataSource = new MatTableDataSource<MMPackage>(PACKAGES);
  selection = new SelectionModel<MMPackage>(true, []);

  ngOnInit() {
    this.api.getMagicMirrorPackages().subscribe(data => {
      console.log(data);
    });
  }

  public applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  public isAllSelected(): boolean {
    return this.selection.selected.length === this.dataSource.data.length;
  }

  public masterToggle(): void {
    this.isAllSelected()
      ? this.selection.clear()
      : this.dataSource.data.forEach((row) => this.selection.select(row));
  }

  public checkboxLabel(row?: MMPackage): string {
    if (!row) return `${this.isAllSelected() ? "select" : "deselect"} all`;
    return `${
      this.selection.isSelected(row) ? "deselect" : "select"
    } row ${row.category + 1}`;
  }
}
