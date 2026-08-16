import { Injectable } from '@angular/core';
import { catchError, firstValueFrom, retry } from 'rxjs';
import { BaseAPI } from './base-api';

export interface DoctorCheck {
  status: 'pass' | 'warn' | 'fail';
  category: string;
  check: string;
  hint: string;
}

export interface DoctorReport {
  results: DoctorCheck[];
  failures: number;
  warnings: number;
}

@Injectable({
  providedIn: 'root',
})
export class DoctorApiService extends BaseAPI {
  public run(): Promise<DoctorReport> {
    console.log('Requesting doctor diagnostics');

    return firstValueFrom(
      this.http
        .get<{ code: number; message: DoctorReport }>(this.route('doctor/run'), {
          headers: this.headers(),
        })
        .pipe(retry(1), catchError(this.handleError)),
    ).then((res) => res.message);
  }
}
