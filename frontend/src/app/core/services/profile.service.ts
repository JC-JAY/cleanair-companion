// Profile service — CRUD for user lifestyle profile
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserProfile {
  id: string;
  user_id: string;
  latitude?: number;
  longitude?: number;
  city?: string;
  state: string;
  country: string;
  has_children: boolean;
  has_elderly: boolean;
  has_asthma_respiratory: boolean;
  has_pregnancy: boolean;
  household_size: number;
  home_type: string;
  cooking_fuel: string;
  has_kitchen_exhaust: boolean;
  num_windows: number;
  heating_type: string;
  commute_mode: string;
  commute_distance_km: number;
  budget_level: string;
  available_devices: string[];
}

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private http = inject(HttpClient);
  private _profile$ = new BehaviorSubject<UserProfile | null>(null);
  readonly profile$ = this._profile$.asObservable();

  getProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${environment.apiUrl}/profile/`).pipe(
      tap(p => this._profile$.next(p))
    );
  }

  createProfile(data: Partial<UserProfile>): Observable<UserProfile> {
    return this.http.post<UserProfile>(`${environment.apiUrl}/profile/`, data).pipe(
      tap(p => this._profile$.next(p))
    );
  }

  updateProfile(data: Partial<UserProfile>): Observable<UserProfile> {
    return this.http.patch<UserProfile>(`${environment.apiUrl}/profile/`, data).pipe(
      tap(p => this._profile$.next(p))
    );
  }

  get current(): UserProfile | null { return this._profile$.value; }
}

