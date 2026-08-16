import { Component, OnInit, inject } from '@angular/core';
import { DoctorApiService, DoctorCheck, DoctorReport } from '@/services/api/doctor-api.service';

interface DoctorCategory {
  name: string;
  checks: DoctorCheck[];
}

const CATEGORY_LABELS: Record<string, string> = {
  environment: 'Environment',
  magicmirror: 'MagicMirror',
  dependencies: 'Dependencies',
  database: 'Database',
  packages: 'Packages',
  services: 'Services',
  remote: 'Remote APIs',
};

@Component({
  selector: 'app-doctor',
  templateUrl: './doctor.component.html',
  styleUrls: ['./doctor.component.scss'],
  standalone: false,
})
export class DoctorComponent implements OnInit {
  private api = inject(DoctorApiService);

  public loading = false;
  public error = '';
  public report: DoctorReport | null = null;
  public categories: DoctorCategory[] = [];

  public ngOnInit(): void {
    this.run();
  }

  public run(): void {
    this.loading = true;
    this.error = '';

    this.api
      .run()
      .then((report) => {
        this.report = report;
        this.categories = this.groupByCategory(report.results);
      })
      .catch((error) => {
        this.error = String(error?.message ?? error);
      })
      .finally(() => {
        this.loading = false;
      });
  }

  public get passed(): number {
    return this.report ? this.report.results.length - this.report.failures - this.report.warnings : 0;
  }

  private groupByCategory(checks: DoctorCheck[]): DoctorCategory[] {
    const grouped = new Map<string, DoctorCheck[]>();

    for (const check of checks) {
      const existing = grouped.get(check.category);

      if (existing) {
        existing.push(check);
      } else {
        grouped.set(check.category, [check]);
      }
    }

    return Array.from(grouped, ([name, categoryChecks]) => ({
      name: CATEGORY_LABELS[name] ?? name,
      checks: categoryChecks,
    }));
  }
}
