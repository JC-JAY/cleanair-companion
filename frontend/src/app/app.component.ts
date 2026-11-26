// Root app component — shell with nav, AQI header, router outlet, and copyright footer
import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

import { AuthService } from './core/services/auth.service';
import { AqiBadgeComponent } from './shared/components/aqi-badge/aqi-badge.component';

@Component({
  selector: 'ca-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet, RouterLink, RouterLinkActive,
    MatToolbarModule, MatSidenavModule, MatListModule,
    MatIconModule, MatButtonModule, MatBadgeModule, MatDividerModule,
    TranslateModule,
    AqiBadgeComponent,
  ],
  template: `
    <mat-sidenav-container class="app-container" fullscreen>
      <mat-sidenav #sidenav mode="over" [fixedInViewport]="true" class="sidenav">
        <mat-nav-list>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>{{ 'nav.dashboard' | translate }}</span>
          </a>
          <a mat-list-item routerLink="/plan" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>event_available</mat-icon>
            <span matListItemTitle>{{ 'nav.dailyPlan' | translate }}</span>
          </a>
          <a mat-list-item routerLink="/chat" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>auto_awesome</mat-icon>
            <span matListItemTitle>{{ 'nav.chat' | translate }}</span>
          </a>
          <a mat-list-item routerLink="/community" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>groups</mat-icon>
            <span matListItemTitle>{{ 'nav.community' | translate }}</span>
          </a>
          <a mat-list-item routerLink="/alerts" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>notifications</mat-icon>
            <span matListItemTitle>{{ 'nav.alerts' | translate }}</span>
          </a>
          <a mat-list-item routerLink="/settings" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>settings</mat-icon>
            <span matListItemTitle>{{ 'nav.settings' | translate }}</span>
          </a>
          <mat-divider></mat-divider>
          <a mat-list-item (click)="logout(); sidenav.close()">
            <mat-icon matListItemIcon>refresh</mat-icon>
            <span matListItemTitle>Restart Session</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>

      <mat-sidenav-content>
        <mat-toolbar color="primary" class="app-toolbar">
          <button mat-icon-button (click)="sidenav.toggle()" aria-label="Open menu">
            <mat-icon>menu</mat-icon>
          </button>
          <span class="toolbar-title">
            <mat-icon class="leaf-icon">eco</mat-icon>
            CleanAir Companion
          </span>
          <span class="spacer"></span>
          <ca-aqi-badge></ca-aqi-badge>
        </mat-toolbar>

        <main class="app-content" role="main">
          <router-outlet></router-outlet>
        </main>

        <!-- Non-medical disclaimer banner -->
        <div class="disclaimer-bar" role="note" aria-label="Disclaimer">
          <mat-icon inline>info</mat-icon>
          {{ 'common.disclaimer' | translate }}
        </div>

        <!-- Global Footer with Copyright -->
        <footer class="app-footer">
          <div class="footer-content">
            <div class="footer-row-brand">
              <mat-icon class="footer-leaf">eco</mat-icon>
              <span class="footer-title">CleanAir Companion</span>
              <span class="footer-tag">· Urban Smog &amp; Winter Inversion Assistant</span>
            </div>
            <div class="footer-row-meta">
              <span>Powered by <strong>Google Gemini 1.5</strong> &amp; <strong>text-embedding-004</strong></span>
              <span class="dot-sep">•</span>
              <span>CPCB &amp; Open-Meteo Air Quality Standards</span>
              <span class="dot-sep">•</span>
              <span>Maharashtra (Pune / Mulshi Region)</span>
            </div>
            <div class="footer-copyright">
              © 2026 CleanAir Companion. All rights reserved.
            </div>
          </div>
        </footer>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .app-container { height: 100vh; }
    .sidenav { width: 260px; }
    .app-toolbar { position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .toolbar-title { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 18px; }
    .leaf-icon { color: #a3c853; }
    .spacer { flex: 1; }
    .app-content { padding: 16px; min-height: calc(100vh - 180px); }
    .disclaimer-bar {
      background: #fff8e1; color: #5d4037;
      padding: 10px 16px; font-size: 12px; text-align: center;
      border-top: 1px solid #ffe082;
      display: flex; align-items: center; justify-content: center; gap: 6px;
    }
    .active { background: rgba(0,0,0,.08); border-radius: 4px; }

    /* Footer styling */
    .app-footer {
      background: #1e293b;
      color: #94a3b8;
      padding: 24px 16px 20px 16px;
      font-size: 13px;
    }
    .footer-content {
      max-width: 1040px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      text-align: center;
    }
    .footer-row-brand {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #f8fafc;
      font-size: 15px;
    }
    .footer-leaf { color: #4ade80; }
    .footer-title { font-weight: 700; }
    .footer-tag { color: #94a3b8; font-size: 13px; }
    .footer-row-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      flex-wrap: wrap;
      justify-content: center;
    }
    .footer-row-meta strong { color: #e2e8f0; }
    .dot-sep { color: #475569; }
    .footer-copyright {
      font-size: 12px;
      color: #64748b;
      margin-top: 4px;
    }
  `],
})
export class AppComponent implements OnInit {
  private auth = inject(AuthService);
  private translate = inject(TranslateService);

  ngOnInit() {
    const savedLang = localStorage.getItem('lang') || 'en';
    this.translate.use(savedLang);
  }

  logout() {
    this.auth.logout();
  }
}
