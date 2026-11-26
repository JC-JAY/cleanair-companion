// Root app component — shell with nav, AQI header, and router outlet
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
            <mat-icon matListItemIcon>chat</mat-icon>
            <span matListItemTitle>{{ 'nav.chat' | translate }}</span>
          </a>
          <a mat-list-item routerLink="/community" routerLinkActive="active" (click)="sidenav.close()">
            <mat-icon matListItemIcon>group</mat-icon>
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
            <mat-icon matListItemIcon>logout</mat-icon>
            <span matListItemTitle>{{ 'nav.logout' | translate }}</span>
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
          {{ 'common.disclaimer' | translate }}
        </div>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .app-container { height: 100vh; }
    .sidenav { width: 260px; }
    .app-toolbar { position: sticky; top: 0; z-index: 100; }
    .toolbar-title { display: flex; align-items: center; gap: 8px; font-weight: 600; }
    .leaf-icon { color: #a3c853; }
    .spacer { flex: 1; }
    .app-content { padding: 16px; min-height: calc(100vh - 128px); }
    .disclaimer-bar {
      background: #fff8e1; color: #5d4037;
      padding: 8px 16px; font-size: 12px; text-align: center;
      border-top: 1px solid #ffe082;
    }
    .active { background: rgba(0,0,0,.08); border-radius: 4px; }
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

