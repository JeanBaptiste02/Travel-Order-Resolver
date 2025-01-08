import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class YatraService {
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  processMessage(sentence: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/process_message`, { sentence });
  }
}
