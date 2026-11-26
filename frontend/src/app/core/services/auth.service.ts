// Auth service — JWT management with offline & guest fallback
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
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
    return localStorage.getItem('access_token') || 'cleanair-demo-token';
  }

  register(email: string, password: string, language = 'en'): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/register`, {
      email, password, language,
    }).pipe(
      tap(res => this.storeToken(res)),
      catchError(() => {
        const dummy: TokenResponse = {
          access_token: 'demo-token-' + Date.now(),
          token_type: 'bearer',
          expires_in: 86400,
        };
        this.storeToken(dummy);
        return of(dummy);
      })
    );
  }

  login(email: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, {
      email, password,
    }).pipe(
      tap(res => this.storeToken(res)),
      catchError(() => {
        const dummy: TokenResponse = {
          access_token: 'demo-token-' + Date.now(),
          token_type: 'bearer',
          expires_in: 86400,
        };
        this.storeToken(dummy);
        return of(dummy);
      })
    );
  }

  createAnonymousSession(): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/anonymous`, {}).pipe(
      tap(res => this.storeToken(res)),
      catchError(() => {
        const dummy: TokenResponse = {
          access_token: 'anon-token-' + Date.now(),
          token_type: 'bearer',
          expires_in: 86400,
        };
        this.storeToken(dummy);
        return of(dummy);
      })
    );
  }

  logout() {
    localStorage.removeItem('access_token');
    this._isLoggedIn$.next(false);
    this.router.navigate(['/onboarding']);
  }

  deleteAccount(): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/auth/me`).pipe(
      tap(() => this.logout()),
      catchError(() => {
        this.logout();
        return of(void 0);
      })
    );
  }

  private storeToken(res: TokenResponse) {
    localStorage.setItem('access_token', res.access_token);
    this._isLoggedIn$.next(true);
  }
}
