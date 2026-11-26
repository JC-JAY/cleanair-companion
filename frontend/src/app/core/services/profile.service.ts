// Profile service — CRUD with local persistence & offline fallback
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserProfile {
  id?: string;
  user_id?: string;
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

const DEFAULT_PROFILE: UserProfile = {
  city: 'Pune',
  state: 'Maharashtra',
  country: 'India',
  latitude: 18.52,
  longitude: 73.85,
  household_size: 3,
  has_children: true,
  has_elderly: false,
  has_asthma_respiratory: true,
  has_pregnancy: false,
  home_type: 'apartment',
  cooking_fuel: 'lpg',
  has_kitchen_exhaust: true,
  num_windows: 4,
  heating_type: 'none',
  commute_mode: 'two_wheeler_petrol',
  commute_distance_km: 10,
  budget_level: 'medium',
  available_devices: ['n95_mask', 'purifier'],
};

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private http = inject(HttpClient);
  private _profile$ = new BehaviorSubject<UserProfile | null>(this.loadSavedProfile());
  readonly profile$ = this._profile$.asObservable();

  private loadSavedProfile(): UserProfile {
    try {
      const saved = localStorage.getItem('user_profile');
      return saved ? JSON.parse(saved) : DEFAULT_PROFILE;
    } catch {
      return DEFAULT_PROFILE;
    }
  }

  getProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${environment.apiUrl}/profile/`).pipe(
      tap(p => {
        localStorage.setItem('user_profile', JSON.stringify(p));
        this._profile$.next(p);
      }),
      catchError(() => {
        const p = this.loadSavedProfile();
        this._profile$.next(p);
        return of(p);
      })
    );
  }

  createProfile(data: Partial<UserProfile>): Observable<UserProfile> {
    const full: UserProfile = { ...DEFAULT_PROFILE, ...data };
    localStorage.setItem('user_profile', JSON.stringify(full));
    this._profile$.next(full);

    return this.http.post<UserProfile>(`${environment.apiUrl}/profile/`, data).pipe(
      tap(p => {
        localStorage.setItem('user_profile', JSON.stringify(p));
        this._profile$.next(p);
      }),
      catchError(() => of(full))
    );
  }

  updateProfile(data: Partial<UserProfile>): Observable<UserProfile> {
    const current = this._profile$.value || DEFAULT_PROFILE;
    const updated = { ...current, ...data };
    localStorage.setItem('user_profile', JSON.stringify(updated));
    this._profile$.next(updated);

    return this.http.patch<UserProfile>(`${environment.apiUrl}/profile/`, data).pipe(
      tap(p => {
        localStorage.setItem('user_profile', JSON.stringify(p));
        this._profile$.next(p);
      }),
      catchError(() => of(updated))
    );
  }

  get current(): UserProfile {
    return this._profile$.value || this.loadSavedProfile();
  }
}
