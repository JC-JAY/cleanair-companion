// Auth service — JWT management and anonymous session support
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _isLoggedIn$ = new BehaviorSubject<boolean>(this.hasToken());
  readonly isLoggedIn$ = this._isLoggedIn$.asObservable();

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  get token(): string | null {
    return localStorage.getItem('access_token');
  }

  register(email: string, password: string, language = 'en'): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/register`, {
      email, password, language,
    }).pipe(tap(res => this.storeToken(res)));
  }

  login(email: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, {
      email, password,
    }).pipe(tap(res => this.storeToken(res)));
  }

  createAnonymousSession(): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/anonymous`, {})
      .pipe(tap(res => this.storeToken(res)));
  }

  logout() {
    localStorage.removeItem('access_token');
    this._isLoggedIn$.next(false);
    this.router.navigate(['/onboarding']);
  }

  deleteAccount(): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/auth/me`).pipe(
      tap(() => this.logout())
    );
  }

  private storeToken(res: TokenResponse) {
    localStorage.setItem('access_token', res.access_token);
    this._isLoggedIn$.next(true);
  }
}

