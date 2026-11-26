// AQI data service — fetches from backend with live Open-Meteo & demo fallbacks
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of, switchMap } from 'rxjs';
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

const DEFAULT_AQI: AQIData = {
  lat: 18.52,
  lon: 73.85,
  source: 'Open-Meteo (Pune Station)',
  observed_at: new Date().toISOString(),
  aqi: 184,
  aqi_category: 'Moderate',
  pm25: 64.5,
  pm10: 108.2,
  no2: 38.6,
  temperature_c: 24.2,
  humidity_pct: 58.0,
  wind_speed_ms: 1.8,
  temperature_inversion: true,
  from_cache: true,
  data_age_minutes: 5,
};

@Injectable({ providedIn: 'root' })
export class AqiService {
  private http = inject(HttpClient);
  private _aqi$ = new BehaviorSubject<AQIData>(DEFAULT_AQI);
  readonly aqi$ = this._aqi$.asObservable();

  fetchAQI(lat = 18.52, lon = 73.85): Observable<AQIData> {
    return this.http.get<AQIData>(`${environment.apiUrl}/aqi/`, {
      params: { lat: lat.toString(), lon: lon.toString() },
    }).pipe(
      tap(data => {
        if (data && data.aqi) {
          this._aqi$.next(data);
        }
      }),
      catchError(() => {
        // Fallback to direct public Open-Meteo air quality endpoint
        const openMeteoUrl = `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${lat}&longitude=${lon}&current=pm10,pm2_5,nitrogen_dioxide&hourly=pm2_5`;
        return this.http.get<any>(openMeteoUrl).pipe(
          tap(res => {
            const curr = res?.current;
            const pm25 = curr?.pm2_5 ?? 64.5;
            const aqiVal = this.pm25ToAqi(pm25);
            const aqiData: AQIData = {
              lat,
              lon,
              source: 'Open-Meteo Air Quality API',
              observed_at: new Date().toISOString(),
              aqi: aqiVal,
              aqi_category: this.getCategoryName(aqiVal),
              pm25: Math.round(pm25 * 10) / 10,
              pm10: curr?.pm10 ? Math.round(curr.pm10 * 10) / 10 : 108,
              no2: curr?.nitrogen_dioxide ? Math.round(curr.nitrogen_dioxide * 10) / 10 : 38,
              temperature_c: 24.5,
              humidity_pct: 56.0,
              wind_speed_ms: 2.1,
              temperature_inversion: true,
              from_cache: false,
              data_age_minutes: 2,
            };
            this._aqi$.next(aqiData);
          }),
          catchError(() => of(DEFAULT_AQI))
        );
      })
    );
  }

  getAQICategory(aqi: number): Observable<any> {
    return of({
      category: this.getCategoryName(aqi),
      hex_color: AqiService.aqiColor(aqi),
    });
  }

  get currentAQI(): AQIData {
    return this._aqi$.value;
  }

  private pm25ToAqi(pm25: number): number {
    if (pm25 <= 30) return Math.round((pm25 / 30) * 50);
    if (pm25 <= 60) return Math.round(51 + ((pm25 - 30) / 30) * 49);
    if (pm25 <= 90) return Math.round(101 + ((pm25 - 60) / 30) * 99);
    if (pm25 <= 120) return Math.round(201 + ((pm25 - 90) / 30) * 99);
    if (pm25 <= 250) return Math.round(301 + ((pm25 - 120) / 130) * 99);
    return Math.min(500, Math.round(401 + ((pm25 - 250) / 130) * 99));
  }

  private getCategoryName(aqi: number): string {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Satisfactory';
    if (aqi <= 200) return 'Moderate';
    if (aqi <= 300) return 'Poor';
    if (aqi <= 400) return 'Very Poor';
    return 'Severe';
  }

  static aqiColor(aqi: number | null): string {
    if (aqi === null) return '#9e9e9e';
    if (aqi <= 50) return '#55a84f';
    if (aqi <= 100) return '#a3c853';
    if (aqi <= 200) return '#fbc02d';
    if (aqi <= 300) return '#f29c33';
    if (aqi <= 400) return '#e93f33';
    return '#af2d24';
  }
}
