import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class YatraService {
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  detectLanguage(sentence: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/detect_language`, { sentence });
  }

  detectIntention(sentence: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/detect_intention`, {
      sentence,
    });
  }

  predictEntities(sentence: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/predict_entities`, {
      sentence,
    });
  }

  findPath(depart: string, arrivee: string): Observable<any> {
    const body = { depart, arrivée: arrivee };
    return this.http.post<any>(`${this.baseUrl}/find_path`, body);
  }
}
