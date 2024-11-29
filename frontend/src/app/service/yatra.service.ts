import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class YatraService {
  private apiUrl = 'http://127.0.0.1:5000/find_path';

  constructor(private http: HttpClient) {}

  findPath(depart: string, arrivee: string): Observable<any> {
    const body = {
      depart: depart,
      arrivée: arrivee,
    };
    return this.http.post<any>(this.apiUrl, body);
  }
}
