import { Injectable } from '@angular/core';
import { catchError, firstValueFrom, retry } from 'rxjs';
import { BaseAPI } from './base-api';

export interface EnvVarInfo {
  name: string;
  description: string;
}

@Injectable({
  providedIn: 'root',
})
export class EnvApiService extends BaseAPI {
  public getDescriptions(): Promise<EnvVarInfo[]> {
    return firstValueFrom(
      this.http
        .get<{ code: number; message: EnvVarInfo[] }>(this.route('env/describe'), {
          headers: this.headers(),
        })
        .pipe(retry(1), catchError(this.handleError)),
    ).then((res) => res.message);
  }
}
