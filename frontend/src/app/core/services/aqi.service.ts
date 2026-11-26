// AQI data service — fetches from backend API
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface AQIData {
  lat: number;
  lon: number;
  source: string;
  observed_at: string;
  aqi: number | null;
  aqi_category: string | null;
  pm25: number | null;
  pm10: number | null;
  no2: number | null;
  temperature_c: number | null;
  humidity_pct: number | null;
  wind_speed_ms: number | null;
  temperature_inversion: boolean;
  from_cache: boolean;
  data_age_minutes: number | null;
}

@Injectable({ providedIn: 'root' })
export class AqiService {
  private http = inject(HttpClient);
  private _aqi$ = new BehaviorSubject<AQIData | null>(null);
  readonly aqi$ = this._aqi$.asObservable();

  fetchAQI(lat: number, lon: number): Observable<AQIData> {
    return this.http.get<AQIData>(`${environment.apiUrl}/aqi/`, {
      params: { lat: lat.toString(), lon: lon.toString() },
    }).pipe(
      tap(data => this._aqi$.next(data)),
      catchError(err => {
        console.error('AQI fetch failed', err);
        return of(null as any);
      })
    );
  }

  getAQICategory(aqi: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/aqi/category`, { params: { aqi: aqi.toString() } });
  }

  get currentAQI(): AQIData | null {
    return this._aqi$.value;
  }

  /** CPCB colour for an AQI value */
  static aqiColor(aqi: number | null): string {
    if (aqi === null) return '#9e9e9e';
    if (aqi <= 50)  return '#55a84f';
    if (aqi <= 100) return '#a3c853';
    if (aqi <= 200) return '#fff833';
    if (aqi <= 300) return '#f29c33';
    if (aqi <= 400) return '#e93f33';
    return '#af2d24';
  }
}

